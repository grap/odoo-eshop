from flask import flash, render_template, request, redirect
from flask_babel import gettext as _

from ..application import app
from ..models.models import execute_odoo_command
from ..models.res_company import get_current_company
from ..models.res_partner import (
    get_current_partner,
    get_current_partner_id,
)
from ..models.sale_order import (
    get_current_sale_order,
    get_sale_order,
)
from ..models.payment_transaction import (
    get_transaction,
    get_transaction_status,
)
from ..tools.auth import requires_auth
from ..tools.web import redirect_url_for
from ..tools.config import conf

import requests

# ############################################################################
# Payment Route
# ############################################################################
@app.route("/payment")
@requires_auth
def payment():
    sale_order = get_current_sale_order()
    partner = get_current_partner()
    return render_template("payment.html", partner=partner, sale_order=sale_order)


# Confirm SO
# Create invoice and pay with wallet
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

# Launch payment with Mollie
@app.route("/payment_validation_online/<int:sale_order_id>")
@requires_auth
def payment_validation_online(sale_order_id):
    # 0. Get infos
    sale_order = get_current_sale_order()

    odoo_base_url = str(
        "http://" + conf.get("odoo", "host") + ":" + conf.get("odoo", "port")
    )
    url = str(odoo_base_url + "/api/sale_generate_payment_link/")
    data = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {"sale_id": sale_order.id},
    } 

    resp = requests.post(url, json=data)
    payment_url = resp.json().get('result')['payment_url']


    # Gérer les erreurs

    # if invoice_online_payment == "error":
    #     flash(_("Error while confirming your payment."), "danger")
    #     return redirect_url_for("payment")
    # else:
    return render_template("payment_online.html", payment_url=payment_url)
    # return redirect(payment_url)

# Retrieve page after Mollie payment
@app.route("/payment_validation_online/status/<int:sale_id>/<int:transaction_id>")
@requires_auth
def payment_validation_online_status(sale_id, transaction_id):
    '''
        Retrieve transaction status [draft, pending, authorized, done, cancel, error]
        1. If it's ok, create invoice, payment and reconcile them
        2. Then give transaction status to template
    '''
    transaction = get_transaction(transaction_id)
    transaction_status = get_transaction_status(transaction_id)
    sale_order = get_sale_order(sale_id)

    if not transaction_status:
        return render_template("404.html")

    # If payment is OK → confirm SO and create Invoice
    elif transaction_status in ['authorized', 'done']:
        
        confirm_order = execute_odoo_command(
            "sale.order",
            "eshop_confirm_sale_order",
            get_current_partner_id(),
        )
        if not confirm_order:
            flash(_("Error while confirming your sale order."), "danger")
            return render_template("200.html")
        else:
            invoice_id = execute_odoo_command(
                "sale.order",
                "eshop_invoice_online_payment",
                sale_order.id,
                transaction.id,
            )

            return render_template("payment_online.html", status=transaction_status)

    return render_template("payment_online.html", status=transaction_status)

@app.route("/sale_confirmed/<string:recovery_name>")
@requires_auth
def sale_confirmed(recovery_name):
    return render_template("sale_confirmed.html", recovery_name=recovery_name)




