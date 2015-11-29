#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Lib
# import math

# Extra Lib
from flask import session
from flask.ext.babel import gettext as _

# Custom Tools
from ..tools.erp import openerp
from .res_company import get_current_company
# from .models import get_openerp_object
# from ..tools.config import conf


# Tools Function
def sanitize_qty(quantity):
    try:
        quantity = float(quantity.replace(',', '.').strip())
    except ValueError:
        return {
            'state': 'danger',
            'message': _("'%(qty)s' is not a valid quantity.", qty=quantity)}
    if quantity == 0:
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
def get_current_sale_order_id():
    """Return current order id, or False if not Found"""
    return openerp.SaleOrder.eshop_get_current_sale_order_id(
        session.get('partner_id', False))


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
    sale_order = get_current_sale_order_id
    openerp.SaleOrder.write([sale_order.id], {'note': note})
    sale_order = get_current_sale_order()
    return {
        'state': 'success',
        'note': sale_order.note,
        'message': _("Your comment has been successfully updated.")}


# ############################################################################
# I/O OpenERP - Sale Order Line
# ############################################################################
def set_quantity(product_id, quantity):
    sanitize = sanitize_qty(quantity)
    company = get_current_company()
    if sanitize['state'] != 'success':
        return sanitize
    res = openerp.SaleOrder.eshop_set_quantity(
        session.get('partner_id', False), product_id, sanitize['quantity'])

    res['state'] = res['changed'] and 'warning' or 'success',

    if company.eshop_vat_included:
        res['amount_line'] = res['price_subtotal_taxinc']
        res['amount_total_header'] = res['amount_total']
        res['minimum_ok'] = (
            res['amount_total'] >= company.eshop_minimum_price)
    else:
        res['amount_line'] = res['price_subtotal']
        res['amount_total_header'] = res['amount_untaxed']
        res['minimum_ok'] = (
            res['amount_untaxed'] >= company.eshop_minimum_price)
    return res


def delete_sale_order_line(line_id):
    sale_order = get_current_sale_order()
    if len(sale_order.order_line) > 1:
        for order_line in sale_order.order_line:
            if order_line.id == line_id:
                order_line.unlink()
    else:
        openerp.SaleOrder.unlink(sale_order.id)


# ############################################################################
# OBSOLETE
# ############################################################################

# def add_quantity(product_id, quantity):
#    res = openerp.SaleOrder.eshop_add_quantity(
#        session.get('partner_id', False), product_id, quantity)

# def compute_quantity_discount(product, quantity):
#    print "compute_quantity_discount"
#    print product
#    print quantity
#    quantity = float(quantity)
#    if quantity <= product.eshop_minimum_qty:
#        if product.eshop_unpacking_qty < product.eshop_minimum_qty:
#            # TODO IMPROVE ME
#            return product.eshop_unpacking_qty, -20
#        else:
#            return product.eshop_minimum_qty, 0
#    else:
#        digit = len(
#            str(float(product.eshop_rounded_qty)
#                - int(product.eshop_rounded_qty)).split('.')[1])
#        division = float(quantity) / product.eshop_rounded_qty
#        if division % 1 == 0:
#            return quantity, 0
#        else:
#            return round(
#                math.ceil(division) * product.eshop_rounded_qty, digit), 0

# def change_product_qty(quantity, mode, product_id=None, line_id=None):
#    """ Mode: can be 'add' or 'set'"""
#    res = sanitize_qty(quantity)
#    if not res['state'] == 'success':
#        return res

#    line = False

#    if product_id:
#        product = get_openerp_object('product.product', product_id)
#        sale_order = load_sale_order()
#        if not sale_order:
#            sale_order = create_sale_order()
#        for sol in sale_order.order_line:
#            if sol.product_id.id == product_id:
#                line = sol
#                break
#    else:
#        line = openerp.SaleOrderLine.browse(line_id)
#        sale_order = line.order_id
#        product = get_openerp_object('product.product', line.product_id.id)

#    uom = get_openerp_object('product.uom', product.uom_id)

#    if not line:
#        # Create New Order Line
#        print res
#        new_quantity, discount = compute_quantity_discount(
#            product, res['quantity'])
#        qty_changed = (new_quantity != res['quantity'])
#        line = openerp.SaleOrderLine.create({
#            'name': product.name,
#            'order_id': sale_order.id,
#            'product_id': product_id,
#            'product_uom_qty': new_quantity,
#            'product_uom': uom.id,
#            'price_unit': product.list_price,
#            'discount': discount,
#            'tax_id': [tax.id for tax in product.taxes_id],
#        })
#    else:
#        if res['quantity'] != 0:
#            # Update Sale Order Line
#            if mode == 'set':
#                desired_qty = res['quantity']
#            else:
#                desired_qty = res['quantity'] + line.product_uom_qty
#            new_quantity, discount = compute_quantity_discount(
#                product, desired_qty)

#            qty_changed = (float(new_quantity) != float(desired_qty))
#            openerp.SaleOrderLine.write([line.id], {
#                'product_uom_qty': new_quantity,
#                'discount': discount,
#            })
#        else:
#            new_quantity = 0
#            if mode == 'set':
#                # Unlink Sale Order Line
#                qty_changed = False
#                openerp.SaleOrderLine.unlink([line.id])
#                line = False
#            else:
#                pass
#                # Weird Case TODO

#    if len(sale_order.order_line) == 1 and new_quantity == 0:
#        openerp.SaleOrder.unlink([sale_order.id])
#        sale_order = False
#        res = {
#            'state': 'success',
#            'quantity': 0,
#            'message': _("Shopping Cart has been successfully deleted.")}
#    elif discount:
#        res = {
#            'state': 'warning',
#            'quantity': new_quantity,
#            'message': _(
#                "The quantity for the product '%(prod)s' is now %(qty)s"
#                "  %(uom)s with a surcharge of %(surcharge)s %.",
#                qty=new_quantity, uom=uom.eshop_description,
#                prod=product.name, surcharge=-discount)}
#    elif qty_changed:
#        res = {
#            'state': 'warning',
#            'quantity': new_quantity,
#            'message': _(
#                "The quantity for the product '%(prod)s' is now %(qty)s"
#                "  %(uom)s, due to minimum / rounded quantity rules.",
#                qty=new_quantity, uom=uom.eshop_description,
#                prod=product.name)}
#    else:
#        res = {
#            'state': 'success',
#            'quantity': new_quantity,
#            'message': _(
#                "You have now %(qty)s %(uom)s of product '%(prod)s'"
#                " in your shopping cart.",
#                qty=new_quantity, uom=uom.eshop_description,
#                prod=product.name)}

#    company = get_openerp_object(
#        'res.company', int(conf.get('openerp', 'company_id')))

#    res.update({
#        'price_subtotal': currency(
#            line.price_subtotal if (sale_order and line) else 0),
#        'amount_untaxed': currency(
#            sale_order.amount_untaxed if sale_order else 0),
#        'amount_tax': currency(
#            sale_order.amount_tax if sale_order else 0),
#        'amount_total': currency(
#            sale_order.amount_total) if sale_order else 0,
#        'minimum_ok': (
#            company.eshop_vat_included and
#            (sale_order.amount_total >= company.eshop_minimum_price) or
#            (sale_order.amount_untaxed >= company.eshop_minimum_price))
#    })
#    if company.eshop_vat_included:
#        res['amount_total_header'] = currency(
#            sale_order.amount_total) if sale_order else 0
#    else:
#        res['amount_total_header'] = currency(
#            sale_order.amount_untaxed) if sale_order else 0

#    return res
