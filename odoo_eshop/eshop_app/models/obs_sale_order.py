#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Lib
import math

# Extra Lib
from flask import session
from flask.ext.babel import gettext as _

# Custom Tools
from ..tools.config import conf
from ..tools.erp import openerp, uid


def currency(n):
    if not n:
        n = 0
    return ('%.02f' % n).replace('.', ',') + u' €'


def load_sale_order():
    if 'partner_id' not in session:
        return None
    sale_orders = openerp.SaleOrder.browse([
        ('partner_id', '=', session['partner_id']),
        ('user_id', '=', uid),
        ('state', '=', 'draft'),
    ])
    if not sale_orders:
        return None
    return sale_orders[0]


def create_sale_order():
    partner = openerp.ResPartner.browse(session['partner_id'])
    if partner.property_product_pricelist:
        pricelist_id = partner.property_product_pricelist.id
    else:
        shop = openerp.SaleShop.browse(conf.get('openerp', 'shop_id'))
        pricelist_id = shop.pricelist_id.id
    sale_order = openerp.SaleOrder.create({
        'partner_id': session['partner_id'],
        'partner_invoice_id': session['partner_id'],
        'partner_shipping_id': session['partner_id'],
        'shop_id': conf.get('openerp', 'shop_id'),
        'pricelist_id': pricelist_id,
    })
    return sale_order


def delete_sale_order():
    sale_order = load_sale_order()
    if sale_order:
        openerp.SaleOrder.unlink([sale_order.id])


def sanitize_qty(quantity):
    try:
        quantity = float(quantity.replace(',', '.').strip())
    except ValueError:
        return {
            'state': 'danger',
            'message': _("'%(qty)s' is not a valid quantity.", qty=quantity)}
    return {
        'state': 'success',
        'quantity': quantity,
    }


def compute_quantity(product, quantity):
    quantity = float(quantity)
    if quantity <= product.eshop_minimum_qty:
        return product.eshop_minimum_qty
    else:
        digit = len(
            str(float(product.eshop_rounded_qty)
                - int(product.eshop_rounded_qty)).split('.')[1])
        division = float(quantity) / product.eshop_rounded_qty
        if division % 1 == 0:
            return quantity
        else:
            return round(
                math.ceil(division) * product.eshop_rounded_qty, digit)


def change_shopping_cart_note(note):
    sale_order = load_sale_order()
    openerp.SaleOrder.write(
        [sale_order.id], {'note': note})
    sale_order = load_sale_order()
    return {
        'state': 'success',
        'note': sale_order.note,
        'message': _("Your comment has been successfully updated.")}


def change_product_qty(quantity, mode, product_id=None, line_id=None):
    """ Mode: can be 'add' or 'set'"""
    res = sanitize_qty(quantity)
    if not res['state'] == 'success':
        return res

    line = False

    if product_id:
        product = openerp.ProductProduct.browse(product_id)
        sale_order = load_sale_order()
        if not sale_order:
            sale_order = create_sale_order()
        for sol in sale_order.order_line:
            if sol.product_id.id == product_id:
                line = sol
                break
    else:
        line = openerp.SaleOrderLine.browse(line_id)
        sale_order = line.order_id
        product = line.product_id

    if not line:
        # Create New Order Line
        new_quantity = compute_quantity(product, res['quantity'])
        qty_changed = (new_quantity != res['quantity'])
        line = openerp.SaleOrderLine.create({
            'name': product.name,
            'order_id': sale_order.id,
            'product_id': product_id,
            'product_uom_qty': new_quantity,
            'product_uom': product.uom_id.id,
            'price_unit': product.list_price,
            'tax_id': [tax.id for tax in product.taxes_id],
        })
    else:
        if res['quantity'] != 0:
            # Update Sale Order Line
            if mode == 'set':
                desired_qty = res['quantity']
            else:
                desired_qty = res['quantity'] + line.product_uom_qty
            new_quantity = compute_quantity(product, desired_qty)

            qty_changed = (float(new_quantity) != float(desired_qty))
            openerp.SaleOrderLine.write([line.id], {
                'product_uom_qty': new_quantity,
            })
        else:
            new_quantity = 0
            if mode == 'set':
                # Unlink Sale Order Line
                qty_changed = False
                openerp.SaleOrderLine.unlink([line.id])
                line = False
            else:
                pass
                # Weird Case TODO

    if len(sale_order.order_line) == 1 and new_quantity == 0:
        openerp.SaleOrder.unlink([sale_order.id])
        sale_order = False
        res = {
            'state': 'success',
            'quantity': 0,
            'message': _("Shopping Cart has been successfully deleted.")}
    elif qty_changed:
        res = {
            'state': 'warning',
            'quantity': new_quantity,
            'message': _(
                "The new quantity for the product '%(prod)s' is now %(qty)s"
                "  %(uom)s, due to minimum / rounded quantity rules.",
                qty=new_quantity, uom=product.uom_id.eshop_description,
                prod=product.name)}
    else:
        res = {
            'state': 'success',
            'quantity': new_quantity,
            'message': _(
                "You have now %(qty)s %(uom)s of product '%(prod)s'"
                " in your shopping cart.",
                qty=new_quantity, uom=product.uom_id.eshop_description,
                prod=product.name)}

    res.update({
        'price_subtotal': currency(
            line.price_subtotal if (sale_order and line) else 0),
        'amount_untaxed': currency(
            sale_order.amount_untaxed if sale_order else 0),
        'amount_tax': currency(
            sale_order.amount_tax if sale_order else 0),
        'amount_total': currency(
            sale_order.amount_total) if sale_order else 0,
        'minimum_ok': (
            session['eshop_vat_included'] and
            (sale_order.amount_total >= session['eshop_minimum_price']) or
            (sale_order.amount_untaxed >= session['eshop_minimum_price']))
    })
    if session.get('eshop_vat_included'):
        res['amount_total_header'] = currency(
            sale_order.amount_total) if sale_order else 0
    else:
        res['amount_total_header'] = currency(
            sale_order.amount_untaxed) if sale_order else 0

    return res
