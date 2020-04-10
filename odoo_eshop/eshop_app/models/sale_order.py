# encoding: utf-8

# Extra Lib
from flask.ext.babel import gettext as _

# Custom Tools
from ..models.models import execute_odoo_command, get_odoo_uncached_object
from .res_company import get_current_company
from .res_partner import get_current_partner_id
from .tools import currency


# Tools Function
def sanitize_qty(quantity, allow_null):
    try:
        quantity = float(quantity.replace(',', '.').strip())
    except ValueError:
        return {
            'state': 'danger',
            'message': _("'%(qty)s' is not a valid quantity.", qty=quantity)}
    if not allow_null and quantity == 0:
        return {
            'state': 'danger',
            'message': _("You can not set a null Quantity.")}
    return {
        'state': 'success',
        'quantity': quantity,
    }


# ############################################################################
# I/O Odoo - Sale Order
# ############################################################################
def get_current_sale_order():
    res = get_odoo_uncached_object(
        "sale.order", get_current_partner_id()
    )
    if res:
        return res[0]
    else:
        return False


def get_current_sale_order_lines(order):
    result = get_odoo_uncached_object(
        "sale.order.line", order.id,
    )
    result = result or []
    return result


# ############################################################################
# I/O Odoo - Sale Order Line
# ############################################################################
def set_quantity(product_id, quantity, allow_null, method):
    sanitize = sanitize_qty(quantity, allow_null)
    company = get_current_company()
    if sanitize['state'] != 'success':
        return sanitize

    res = execute_odoo_command(
        "sale.order", "eshop_set_quantity",
        get_current_partner_id(),
        product_id,
        sanitize['quantity'],
        method
    )

    if res['changed'] or (res['discount'] < 0):
        res['state'] = 'warning'
    else:
        res['state'] = 'success'
    res['message'] = '<br />'.join(res['messages'])

    res['is_surcharged'] = res['discount'] < 0
    if company.eshop_vat_included:
        res['amount_line'] = currency(res['price_subtotal_gross'])
        res['amount_total_header'] = currency(res['amount_total'])
        res['minimum_ok'] = (
            res['amount_total'] >= company.eshop_minimum_price)
    else:
        res['amount_line'] = currency(res['price_subtotal'])
        res['amount_total_header'] = currency(res['amount_untaxed'])
        res['minimum_ok'] = (
            res['amount_untaxed'] >= company.eshop_minimum_price)
    return res
