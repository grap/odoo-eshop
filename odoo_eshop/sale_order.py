#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from flask import session
from config import conf
from erp import openerp, uid


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


def add_product(product, quantity):
    sale_order = load_sale_order()
    if not sale_order:
        sale_order = create_sale_order()
    sale_order_line = False
    for sol in sale_order.order_line:
        if sol.product_id.id == product.id:
            sale_order_line = sol
            break
    if not sale_order_line:
        openerp.SaleOrderLine.create({
            'name': product.name,
            'order_id': sale_order.id,
            'product_id': product.id,
            'product_uom_qty': quantity,
            'product_uom': product.uom_id.id,
            'price_unit': product.list_price,
            'tax_id': [tax.id for tax in product.taxes_id],
            })
    else:
        openerp.SaleOrderLine.write(sale_order_line.id, {
            'product_uom_qty': quantity + sale_order_line.product_uom_qty,
            })
