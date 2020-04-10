#! /usr/bin/env python

# Standard Libs
import logging
from datetime import datetime
import pytz

# Extra Libs
from flask import request, render_template, flash

from flask.ext.babel import gettext as _

# Custom Tools
from ..application import (
    app,
    babel,
)

from ..tools.web import redirect_url_for
from ..tools.config import conf
from ..tools.auth import requires_connection, requires_auth
from ..tools.erp import tz

# Custom Models
from ..models.models import get_odoo_object, execute_odoo_command
from ..models.tools import currency

from ..models.res_partner import (
    get_current_partner,
    get_current_partner_id
)
from ..models.res_company import get_current_company

from ..models.sale_order import get_current_sale_order


# ############################################################################
# Home Route
# ############################################################################
@app.route("/")
@requires_connection
def home():
    if get_current_partner_id():
        return redirect_url_for('home_logged')
    return render_template('home.html')


@app.route("/home_logged.html")
@requires_auth
def home_logged():
    company = get_current_company()
    if company.eshop_manage_recovery_moment:
        pending_moment_groups = execute_odoo_command(
            "sale.recovery.moment.group",
            "browse",
            [('state', 'in', 'pending_sale')]
        )
        futur_moment_groups = execute_odoo_command(
            "sale.recovery.moment.group",
            "browse",
            [('state', 'in', 'futur')]
        )
        pending_moments = execute_odoo_command(
            "sale.recovery.moment",
            "browse",
            [('state', 'in', 'pending_sale')]
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
                flash(_(
                    "It is not possible to buy for the time being,"
                    " You can buy starting at %(day)s %(date)s %(time)s.",
                    day=to_day(min_date), date=to_date(min_date),
                    time=to_time(min_date)), 'warning')
            else:
                flash(_(
                    "It is not possible to buy for the time being,"
                    " but you can see the catalog in the meantime."),
                    'warning')
        elif len(pending_moment_groups) == 1:
            # Display end Date to order
            flash(_(
                "You can buy until %(day)s %(date)s %(time)s.",
                day=to_day(pending_moment_groups[0].max_sale_date),
                date=to_date(pending_moment_groups[0].max_sale_date),
                time=to_time(pending_moment_groups[0].max_sale_date)), 'info')
    else:
        flash(_('Recovery Moment Unset'), 'danger')
    return render_template('home.html')


# ############################################################################
# Technical Routes
# ############################################################################
@app.route("/unavailable_service.html")
@requires_auth
def unavailable_service():
    return render_template('unavailable_service.html')


@app.route(
    "/invalidation_cache/" +
    "<string:key>/<string:model>/<int:id>/")
@requires_connection
def invalidation_cache(key, model, id):
    if key == conf.get('cache', 'invalidation_key'):
        # Invalidate Object cache
        get_odoo_object(str(model), int(id), force_reload=True)
        return render_template('200.html'), 200
    else:
        return render_template('404.html'), 404


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(Exception)
def error(e):
    flash(
        "An unexcepted error occured. Please try again in a while", 'danger')
    logging.exception('an error occured')
    return render_template('500.html'), 500


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
        get_object=get_object, current_partner=current_partner,
        current_company=current_company, current_sale_order=current_sale_order,
        is_vat_included=is_vat_included)


# ############################################################################
# Babel Local Selector
# ############################################################################
@babel.localeselector
def locale_selector():
    return request.accept_languages.best_match(['fr'])


def get_local_date(str_utc_date, schema):
    """From UTC string Datetime, return local datetime"""
    mytz = pytz.timezone(tz)
    utc_date = datetime.strptime(str_utc_date, schema)
    return mytz.fromutc(utc_date)


# ############################################################################
# Template filters
# ############################################################################

@app.template_filter('to_currency')
def compute_currency(amount):
    return currency(amount)


@app.template_filter('float_to_string')
def float_to_string(value):
    if (value % 1) == 0:
        return str(int(value))
    else:
        return str(value).replace('.', ',')


@app.template_filter('surcharge_to_string')
def surcharge_to_string(value):
    if not value:
        return ''
    elif value > 0:
        # Display a Surcharge
        return '(+%s%%)' % float_to_string(value)
    else:
        # Display a discount
        return '(-%s%%)' % float_to_string(value)


@app.template_filter('function_to_eval')
def function_to_eval(arg):
    return arg


@app.template_filter('to_day')
def to_day(arg):
    if ' ' in arg:
        int_day = get_local_date(arg, '%Y-%m-%d %H:%M:%S').strftime('%w')
    else:
        int_day = get_local_date(arg, '%Y-%m-%d').strftime('%w')
    return {
        '0': _('Sunday'),
        '1': _('Monday'),
        '2': _('Tuesday'),
        '3': _('Wednesdsay'),
        '4': _('Thursday'),
        '5': _('Friday'),
        '6': _('Saturday'),
    }[int_day]


@app.template_filter('to_ids')
def to_ids(arg):
    return [x.id for x in arg]


@app.template_filter('to_date')
def to_date(arg):
    if ' ' in arg:
        return get_local_date(arg, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
    else:
        return get_local_date(arg, '%Y-%m-%d').strftime('%d/%m/%Y')


@app.template_filter('to_datetime')
def to_datetime(arg):
    return get_local_date(arg, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %Hh%M')


@app.template_filter('to_time')
def to_time(arg):
    return get_local_date(arg, '%Y-%m-%d %H:%M:%S').strftime('%Hh%M')


# TODO FIXME: Problem with erpeek. Text of field selection unavaible
@app.template_filter('fresh_category')
def fresh_category(value):
    return {
        'extra': _('Extra'),
        '1': _('Category I'),
        '2': _('Category II'),
        '3': _('Category III'),
    }[value]


@app.template_filter('empty_if_null')
def empty_if_null(value):
    return value if value else ''


@app.template_filter('tax_description_per_line')
def tax_description_per_line(line):
    taxes = [get_odoo_object("account.tax", x) for x in line.tax_ids]
    return ', '.join([x.eshop_description for x in taxes])
