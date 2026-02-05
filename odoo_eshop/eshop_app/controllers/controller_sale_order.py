from flask import flash, jsonify, render_template, request
from flask_babel import gettext as _

from ..application import app
from ..models.models import execute_odoo_command
from ..models.res_company import get_current_company
from ..models.res_partner import get_current_partner_id
from ..models.sale_order import (
    get_current_sale_order,
    get_current_sale_order_lines,
    set_quantity,
)
from ..models.tools import currency
from ..tools.auth import requires_auth
from ..tools.web import redirect_url_for


# ############################################################################
# Shopping Cart Management Routes
# ############################################################################
@app.route("/shopping_cart")
@requires_auth
def shopping_cart():
    order = get_current_sale_order()
    if not order:
        return redirect_url_for("home")
    sale_order_lines = get_current_sale_order_lines(order)
    return render_template("shopping_cart.html", sale_order_lines=sale_order_lines)


@app.route("/shopping_cart_eshop_note_update", methods=["POST"])
def shopping_cart_eshop_note_update():
    eshop_note = execute_odoo_command(
        "sale.order",
        "eshop_set_eshop_note",
        get_current_partner_id(),
        request.form["eshop_note"],
    )
    result = {
        "state": "success",
        "eshop_note": eshop_note,
        "message": _("Your comment has been successfully updated."),
    }
    if True:  # request.is_xhr:
        return jsonify(result=result)
    flash(result["message"], result["state"])
    return redirect_url_for("shopping_cart")


@app.route("/shopping_cart_quantity_update", methods=["POST"])
def shopping_cart_quantity_update():
    res = set_quantity(
        int(request.form["product_id"]), request.form["new_quantity"], False, "set"
    )
    if True:  # request.is_xhr:
        return jsonify(result=res)
    flash(res["message"], res["state"])
    return redirect_url_for("shopping_cart")


@app.route("/shopping_cart_delete")
@requires_auth
def shopping_cart_delete():
    execute_odoo_command(
        "sale.order",
        "eshop_delete_current_sale_order",
        get_current_partner_id(),
    )
    flash(_("Your shopping cart has been successfully deleted."), "success")
    return redirect_url_for("home_logged")


@app.route("/shopping_cart_delete_line/<int:line_id>")
@requires_auth
def shopping_cart_delete_line(line_id):
    result = execute_odoo_command(
        "sale.order",
        "eshop_delete_sale_order_line",
        get_current_partner_id(),
        line_id,
    )
    if result == "line_deleted":
        flash(_("The Line has been successfully deleted."), "success")
        return redirect_url_for("shopping_cart")
    else:
        flash(_("Your shopping cart has been deleted."), "success")
        return redirect_url_for("home_logged")


# ############################################################################
# Recovery Moment Place Route
# ############################################################################
@app.route("/recovery_moment_place")
def recovery_moment_place():
    company = get_current_company()
    partner_id = get_current_partner_id()
    #  Get Recovery moment with no limitation
    #       + the ones with limitation where the partner is
    #
    # Search method (instead of browse_by_search) avoid to browse
    # every fields that needs more user access or can be linked 
    # to other module and complexity
    # Side effect : load object on view and add inherit models with eshop_mixin
    recovery_moments = execute_odoo_command(
        "sale.recovery.moment",
        "search",
        ['&',
            '|',
                ("limited_partners_ids", "in", partner_id),
                ("is_limited", "=", False),
            ("state", "=", "pending_sale"),
        ],
        order="min_recovery_date",
    )
    sale_order = get_current_sale_order()
    if (
        company.eshop_minimum_price != 0
        and company.eshop_minimum_price > sale_order.amount_total
    ):
        flash(
            _("You have not reached the ceiling : ")
            + currency(company.eshop_minimum_price),
            "warning",
        )
        return redirect_url_for("shopping_cart")
    return render_template(
        "recovery_moment_place.html", recovery_moments=recovery_moments,
    )


@app.route("/select_recovery_moment/<int:recovery_moment_id>")
@requires_auth
def select_recovery_moment(recovery_moment_id):
    # Add recovery moment to SO
    res_recovery_moment = execute_odoo_command(
        "sale.order",
        "eshop_select_recovery_moment",
        get_current_partner_id(),
        recovery_moment_id,
    )
    recovery_name = get_current_sale_order().recovery_name

    # Full recovery moment
    if res_recovery_moment == "recovery_moment_complete":
        flash(_("The recovery moment is complete." " Please try again."), "danger")
        return redirect_url_for("recovery_moment_place")
    else:
        # Get to payment choice
        return redirect_url_for("payment")
