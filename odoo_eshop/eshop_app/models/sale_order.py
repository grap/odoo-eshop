# encoding: utf-8

# Standard Lib
# import math

# Extra Lib
from flask.ext.babel import gettext as _

# Custom Tools
from ..tools.erp import openerp
from .res_company import get_current_company
from .res_partner import get_current_partner_id
from .models import currency


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
# I/O OpenERP - Sale Order
# ############################################################################
def get_is_vat_included(company, sale_order, partner):
    # # otherwise, return company setting
    return company.eshop_vat_included


def get_current_sale_order_id():
    """Return current order id, or False if not Found"""
    return openerp.SaleOrder.eshop_get_current_sale_order_id(
        get_current_partner_id())


def get_current_sale_order():
    """Return current order, or False if not Found"""
    current_order_id = get_current_sale_order_id()
    if current_order_id:
        return openerp.SaleOrder.browse(current_order_id)
    else:
        return None


def delete_current_sale_order():
    """Delete current order, if exists."""
    current_order_id = get_current_sale_order_id()
    if current_order_id:
        openerp.SaleOrder.unlink([current_order_id])


def change_sale_order_note(note):
    sale_order_id = get_current_sale_order_id()
    openerp.SaleOrder.write([sale_order_id], {'note': note})
    sale_order = get_current_sale_order()
    return {
        'state': 'success',
        'note': sale_order.note,
        'message': _("Your comment has been successfully updated.")}


# ############################################################################
# I/O OpenERP - Sale Order Line
# ############################################################################
def set_quantity(product_id, quantity, allow_null, method):
    sanitize = sanitize_qty(quantity, allow_null)
    company = get_current_company()
    if sanitize['state'] != 'success':
        return sanitize
    res = openerp.SaleOrder.eshop_set_quantity(
        get_current_partner_id(), product_id, sanitize['quantity'],
        method)

    if res['changed'] or (res['discount'] < 0):
        res['state'] = 'warning'
    else:
        res['state'] = 'success'
    res['message'] = '<br />'.join(res['messages'])

    res['is_surcharged'] = res['discount'] < 0
    if get_is_vat_included(company, get_current_sale_order(), False):
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


def delete_sale_order_line(line_id):
    sale_order = get_current_sale_order()
    if len(sale_order.order_line) > 1:
        openerp.SaleOrderLine.unlink([line_id])
    else:
        openerp.SaleOrder.unlink([sale_order.id])
