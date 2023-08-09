import logging
from datetime import datetime

import pytz
from flask import flash, render_template
from flask_babel import gettext as _

from ..application import app
from ..models.models import execute_odoo_command, get_odoo_object
from ..models.res_company import get_current_company
from ..models.res_partner import get_current_partner, get_current_partner_id
from ..models.sale_order import get_current_sale_order
from ..models.tools import currency
from ..tools.auth import requires_auth, requires_connection
from ..tools.config import conf
from ..tools.erp import tz
from ..tools.web import redirect_url_for


# ############################################################################
# Home Route
# ############################################################################
@app.route("/")
@requires_connection
def home():
    if get_current_partner_id():
        return redirect_url_for("home_logged")
    return render_template("home.html")


@app.route("/home_logged.html")
@requires_auth
def home_logged():
    company = get_current_company()
    if company.eshop_manage_recovery_moment:
        pending_moment_groups = execute_odoo_command(
            "sale.recovery.moment.group",
            "browse_by_search",
            [("state", "in", "pending_sale")],
        )
        futur_moment_groups = execute_odoo_command(
            "sale.recovery.moment.group", "browse_by_search", [("state", "in", "futur")]
        )
        pending_moments = execute_odoo_command(
            "sale.recovery.moment",
            "browse_by_search",
            [("state", "in", "pending_sale")],
        )
        if len(pending_moment_groups) == 0:
            if len(pending_moments):
                # nothing to do, shop is working only with moments, no groups
                pass

            elif len(futur_moment_groups) > 0:
                # Not possible to purchase for the time being
                min_date = futur_moment_groups[0].min_sale_date
                for item in futur_moment_groups:
                    min_date = min(min_date, item.min_sale_date)
                flash(
                    _(
                        "It is not possible to buy for the time being,"
                        " You can buy starting at %(day)s %(date)s %(time)s.",
                        day=to_day(min_date),
                        date=to_date(min_date),
                        time=to_time(min_date),
                    ),
                    "warning",
                )
            else:
                flash(
                    _(
                        "It is not possible to buy for the time being,"
                        " but you can see the catalog in the meantime."
                    ),
                    "warning",
                )
        elif len(pending_moment_groups) == 1:
            # Display end Date to order
            flash(
                _(
                    "You can buy until %(day)s %(date)s %(time)s.",
                    day=to_day(pending_moment_groups[0].max_sale_date),
                    date=to_date(pending_moment_groups[0].max_sale_date),
                    time=to_time(pending_moment_groups[0].max_sale_date),
                ),
                "info",
            )
    else:
        flash(_("Recovery Moment Unset"), "danger")
    return render_template("home.html")


# ############################################################################
# Technical Routes
# ############################################################################
@app.route("/unavailable_service.html")
@requires_auth
def unavailable_service():
    return render_template("unavailable_service.html")


@app.route("/invalidation_cache/" + "<string:key>/<string:model>/<int:id>/")
@requires_connection
def invalidation_cache(key, model, id):
    if key == conf.get("cache", "invalidation_key"):
        # Invalidate Object cache
        get_odoo_object(str(model), int(id), force_reload=True)
        return render_template("200.html"), 200
    else:
        return render_template("404.html"), 404


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(Exception)
def error(e):
    flash("An unexcepted error occured. Please try again in a while", "danger")
    logging.exception("an error occured")
    return render_template("500.html"), 500


# ############################################################################
# Context Processor
# ############################################################################
@app.context_processor
def utility_processor():
    def get_object(model_name, id):
        return get_odoo_object(model_name, id)

    def current_partner():
        return get_current_partner()

    def current_company():
        return get_current_company()

    def current_sale_order():
        return get_current_sale_order()

    def is_vat_included():
        return get_current_company().eshop_vat_included

    return dict(
        get_object=get_object,
        current_partner=current_partner,
        current_company=current_company,
        current_sale_order=current_sale_order,
        is_vat_included=is_vat_included,
    )


# ############################################################################
# Babel Local Selector
# ############################################################################
def get_local_date(str_utc_date, schema):
    """From UTC string Datetime, return local datetime"""
    mytz = pytz.timezone(tz)
    utc_date = datetime.strptime(str_utc_date, schema)
    return mytz.fromutc(utc_date)


# ############################################################################
# Template filters
# ############################################################################


@app.template_filter("to_currency")
def compute_currency(amount):
    return currency(amount)


@app.template_filter("float_to_string")
def float_to_string(value):
    if (value % 1) == 0:
        return str(int(value))
    else:
        return str(value).replace(".", ",")


@app.template_filter("surcharge_to_string")
def surcharge_to_string(value):
    if not value:
        return ""
    elif value > 0:
        # Display a Surcharge
        return "(+%s%%)" % float_to_string(value)
    else:
        # Display a discount
        return "(-%s%%)" % float_to_string(value)


@app.template_filter("function_to_eval")
def function_to_eval(arg):
    return arg


@app.template_filter("to_day")
def to_day(arg):
    return {
        0: _("Monday"),
        1: _("Tuesday"),
        2: _("Wednesdsay"),
        3: _("Thursday"),
        4: _("Friday"),
        5: _("Saturday"),
        6: _("Sunday"),
    }[pytz.timezone(tz).fromutc(arg).weekday()]


@app.template_filter("to_ids")
def to_ids(arg):
    return [x.id for x in arg]


@app.template_filter("to_date")
def to_date(arg):
    return pytz.timezone(tz).fromutc(arg).strftime("%d/%m/%Y")


@app.template_filter("to_time")
def to_time(arg):
    return pytz.timezone(tz).fromutc(arg).strftime("%Hh%M")


@app.template_filter("empty_if_null")
def empty_if_null(value):
    return value if value else ""


@app.template_filter("tax_description_per_line")
def tax_description_per_line(line):
    taxes = [get_odoo_object("account.tax", x) for x in line.tax_ids]
    return ", ".join([x.description for x in taxes])
