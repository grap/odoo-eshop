from flask import flash, render_template, request, redirect
from flask_babel import gettext as _

from ..application import app
from ..models.models import execute_odoo_command
from ..models.res_company import get_current_company
from ..models.res_partner import (
    get_current_partner,
    get_current_partner_id,
    get_current_partner_address_check,
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
    if not sale_order:
        return render_template("404.html")    
    partner = get_current_partner()
    partner_address_check = get_current_partner_address_check()
    recovery_name = sale_order.recovery_name
    return render_template("payment.html", partner=partner, sale_order=sale_order, recovery_name=recovery_name, partner_address_check=partner_address_check)


# CONFIRM PAYMENT WITH WALLET
@app.route("/payment_validation_wallet/<int:sale_order_id>")
@requires_auth
def payment_validation_wallet(sale_order_id):
    # 0. Get infos before SO to be validated
    sale_order = get_sale_order(sale_order_id, force_reload=True)
    if not sale_order:
        return render_template("404.html")    
    recovery_name = sale_order.recovery_name

    # 1. Confirm Sale Order
    if sale_order.state != 'sale':    
        confirm_order = execute_odoo_command(
            "sale.order",
            "eshop_confirm_sale_order",
            get_current_partner_id(),
        )
        if not confirm_order:
            flash(_("Error while confirming your sale order."), "danger")
            return redirect_url_for("payment")

    # 2. Create a paid invoice and link to sale
    if sale_order.invoice_status != 'invoiced':
        invoice_with_wallet = execute_odoo_command(
            "sale.order",
            "eshop_invoice_with_wallet",
            sale_order_id,
        )
        if invoice_with_wallet == "error":
            flash(_("Error while confirming your payment."), "danger")
            return redirect_url_for("payment")
    
    return render_template("sale_confirmed.html", recovery_name=recovery_name, command_paid=True)

# CONFIRM PAYMENT WITH MOLLIE
@app.route("/payment_validation_online/<int:sale_order_id>")
@requires_auth
def payment_validation_online(sale_order_id):
    # 0. Get infos
    sale_order = get_current_sale_order()
    if not sale_order:
        return render_template("404.html")

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

    return render_template("payment_online.html", payment_url=payment_url)

# Retrieve page after Mollie payment
@app.route("/payment_validation_online/status/<int:sale_id>/<int:transaction_id>")
@requires_auth
def payment_validation_online_status(sale_id, transaction_id):
    '''
        Retrieve transaction status [draft, pending, authorized, done, cancel, error]
        1. If it's ok, create invoice, payment and reconcile them
        2. Then give transaction status to template
        Idempotent function to access validation page each time
    '''
    transaction = get_transaction(transaction_id)
    transaction_status = get_transaction_status(transaction_id)
    sale_order = get_sale_order(sale_id, force_reload=True)

    if not transaction_status or not sale_order:
        return render_template("404.html")

    # If payment is OK → confirm SO and create Invoice
    elif transaction_status in ['authorized', 'done']:
        
        # Handle confirming SO
        if sale_order.state != 'sale':
            confirm_order = execute_odoo_command(
                "sale.order",
                "eshop_confirm_sale_order",
                get_current_partner_id(),
            )
            if not confirm_order:
                flash(_("Error while confirming your sale order."), "danger")
                return render_template("404.html")

        # Handle creation of Invoice
        if sale_order.invoice_status != 'invoiced':
            invoice_id = execute_odoo_command(
                "sale.order",
                "eshop_invoice_online_payment",
                sale_order.id,
                transaction.id,
            )
        recovery_name = sale_order.recovery_name
        return render_template("sale_confirmed.html", status=transaction_status, recovery_name=recovery_name, command_paid=True)

    else:
        return render_template("sale_confirmed.html", status=transaction_status)

# CONFIRM PAYMENT ON SITE
@app.route("/payment_on_site_validation")
@requires_auth
def payment_on_site_validation():
    # 0. Get infos before SO to be validated
    sale_order = get_current_sale_order()
    if not sale_order:
        return render_template("404.html")
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
        return render_template("sale_confirmed.html", recovery_name=recovery_name, command_paid=False)

