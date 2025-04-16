from flask import flash, jsonify, render_template, request
from flask_babel import gettext as _

from ..application import app
from ..models.models import execute_odoo_command, get_odoo_object
from ..models.res_partner import (
    get_current_partner,
    get_current_partner_id,
)
from ..models.sale_order import (
    get_current_sale_order,
    get_current_sale_order_lines,
)
from ..tools.auth import requires_auth
from ..tools.web import redirect_url_for

# ############################################################################
# Payment Route
# ############################################################################
@app.route("/payment")
@requires_auth
def payment():
    sale_order = get_current_sale_order()
    partner = get_current_partner()
    return render_template("payment.html", partner=partner, sale_order=sale_order)


@app.route("/payment_validation/<int:sale_order_id>")
@requires_auth
def payment_validation(sale_order_id):
    # 0. Get infos before SO to be validated
    sale_order = get_current_sale_order()
    recovery_name = sale_order.recovery_name

    # 1. Confirm Sale Order
    confirm_order = execute_odoo_command(
        "sale.order",
        "eshop_confirm_sale_order",
        get_current_partner_id(),
    )
    if not confirm_order:
        flash(_("Error while confirming your sale order."), "danger")
        return redirect_url_for("payment")
    else:

        # 2. Create a paid invoice and link to sale
        invoice_with_wallet = execute_odoo_command(
            "sale.order",
            "eshop_invoice_with_wallet",
            sale_order_id,
        )
        if invoice_with_wallet == "error":
            flash(_("Error while confirming your payment."), "danger")
            return redirect_url_for("payment")
        else:
            return redirect_url_for("sale_confirmed", recovery_name=recovery_name)

@app.route("/sale_confirmed/<string:recovery_name>")
@requires_auth
def sale_confirmed(recovery_name):
    sale_order = get_current_sale_order()
    return render_template("sale_confirmed.html", recovery_name=recovery_name)
