#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from flask import (
    g,
    session,
    #  render_template,
    #     flash,
)
from config import conf


def load_sale_order():
    session['partner_id']
    sale_orders = g.openerp.SaleOrder.browse([
        ('partner_id', '=', session['partner_id']),
        ('user_id', '=', session['user_id']),
        ('state', '=', 'draft'),
        ])
    if len(sale_orders) > 0:
        session['sale_order_id'] = sale_orders[0].id
        update_header()


def create_sale_order():
    partner = g.openerp.ResPartner.browse(session['partner_id'])
    if partner.property_product_pricelist:
        pricelist_id = partner.property_product_pricelist.id
    else:
        shop = g.openerp.SaleShop.browse(conf.get('openerp', 'shop_id'))
        pricelist_id = shop.pricelist_id.id
    sale_order = g.openerp.SaleOrder.create({
        'partner_id': session['partner_id'],
        'partner_invoice_id': session['partner_id'],
        'partner_shipping_id': session['partner_id'],
        'shop_id': conf.get('openerp', 'shop_id'),
        'pricelist_id': pricelist_id,
        })
    session['sale_order_id'] = sale_order.id
    session['sale_order_total'] = 0
    return sale_order


def add_product(product, quantity):
    if 'sale_order_id' not in session:
        sale_order = create_sale_order()
    else:
        sale_order = g.openerp.SaleOrder.browse(session['sale_order_id'])
    sale_order_line = False
    for sol in sale_order.order_line:
        if sol.product_id.id == product.id:
            sale_order_line = sol
            break
    if not sale_order_line:
        g.openerp.SaleOrderLine.create({
            'name': product.name,
            'order_id': sale_order.id,
            'product_id': product.id,
            'product_uom_qty': quantity,
            'product_uom': product.uom_id.id,
            'price_unit': product.list_price,
            'tax_id': [tax.id for tax in product.taxes_id],
            })
    else:
        g.openerp.SaleOrderLine.write(sale_order_line.id, {
            'product_uom_qty': quantity + sale_order_line.product_uom_qty,
            })
    update_header()


def update_header():
    if 'sale_order_id' in session:
        sale_order = g.openerp.SaleOrder.browse(session['sale_order_id'])
        session['sale_order_total'] = sale_order.amount_total and \
            sale_order.amount_total or 0
    else:
        session['sale_order_total'] = False
