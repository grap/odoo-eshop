from flask import flash, render_template, request, redirect
from flask_babel import gettext as _

from ..application import app
from ..models.models import execute_odoo_command
from ..models.res_partner import (
    get_current_partner,
    get_current_partner_id,
)
from ..models.sale_order import get_current_sale_order

from ..tools.auth import requires_auth
from ..tools.web import redirect_url_for

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
    # 0. Get infos before SO to be validated
    sale_order = get_current_sale_order()

    # 1. Confirm Sale Order
    # confirm_order = execute_odoo_command(
    #     "sale.order",
    #     "eshop_confirm_sale_order",
    #     get_current_partner_id(),
    # )
    # if not confirm_order:
    #     flash(_("Error while confirming your sale order."), "danger")
    #     return redirect_url_for("payment")
        # 2. Create a paid invoice and link to sale
        # invoice_id = execute_odoo_command(
        #     "sale.order",
        #     "eshop_invoice_online_payment",
        #     sale_order_id,
        # )
        

    url = "http://localhost:8016/api/sale_generate_payment_link/"
    data = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {"sale_id": sale_order.id},
        "id": 1
    } 

    # TODO : id 1 ?
    
    resp = requests.post(url, json=data)
    # print(resp.json())

    payment_url = resp.json().get('result')['payment_url']


    # Gérer les erreurs

    # if invoice_online_payment == "error":
    #     flash(_("Error while confirming your payment."), "danger")
    #     return redirect_url_for("payment")
    # else:
    return render_template("payment_online.html", payment_url=payment_url)
    # return redirect(payment_url)

# @app.route("/payment_validation_online/<int:sale_order_id>")
# @requires_auth
# def payment_validation_online(sale_order_id):
#     # 0. Get infos before SO to be validated
#     sale_order = get_current_sale_order()
#     recovery_name = sale_order.recovery_name

#     # 1. Confirm Sale Order
#     confirm_order = execute_odoo_command(
#         "sale.order",
#         "eshop_confirm_sale_order",
#         get_current_partner_id(),
#     )
#     if not confirm_order:
#         flash(_("Error while confirming your sale order."), "danger")
#         return redirect_url_for("payment")
#     else:
#         # 2. Create a paid invoice and link to sale
#         invoice_id = execute_odoo_command(
#             "sale.order",
#             "eshop_invoice_online_payment",
#             sale_order_id,
#         )
        
#         import requests

#         url = "http://localhost:8016/api/generate_payment_link/"
#         data = {
#             "jsonrpc": "2.0",
#             "method": "call",
#             "params": {"invoice_id": invoice_id},
#             "id": 1
#         }

#         resp = requests.post(url, json=data)
#         print(resp.json())

#         payment_url = resp.json().get('result')['payment_url']


#         # Gérer les erreurs

#         # if invoice_online_payment == "error":
#         #     flash(_("Error while confirming your payment."), "danger")
#         #     return redirect_url_for("payment")
#         # else:
#         return render_template("payment_online.html", payment_url=payment_url)
#         # return redirect(payment_url)


@app.route("/sale_confirmed/<string:recovery_name>")
@requires_auth
def sale_confirmed(recovery_name):
    return render_template("sale_confirmed.html", recovery_name=recovery_name)




