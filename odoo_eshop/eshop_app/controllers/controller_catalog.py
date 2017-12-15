#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import hashlib

# Extra Libs
from flask import request, render_template, flash, jsonify

# Custom Tools
from ..application import app

from ..tools.web import redirect_url_for
from ..tools.erp import openerp
from ..tools.auth import requires_auth

from ..models.models import get_openerp_object
from ..models.sale_order import (
    get_current_sale_order,
    get_current_sale_order_id,
    set_quantity,
)


# ############################################################################
# Catalog (Tree View) Routes
# ############################################################################
@app.route('/catalog_tree/', defaults={'category_id': False})
@app.route("/catalog_tree/<int:category_id>")
@requires_auth
def catalog_tree(category_id):

    # Get Child Categories
    category_ids = openerp.eshopCategory.search([
        ('parent_id', '=', category_id)])

    # Get Products
    product_ids = openerp.ProductProduct.search([
        ('eshop_state', '=', 'available'),
        ('eshop_category_id', '=', category_id)], order='name')

    parent_categories = []
    parent = get_openerp_object('eshop.category', category_id)
    # Get Parent Categories
    while parent:
        parent_categories.insert(0, {'id': parent.id, 'name': parent.name})
        parent = get_openerp_object('eshop.category', parent.parent_id)

    return render_template(
        'catalog_tree.html', parent_categories=parent_categories,
        category_ids=category_ids, product_ids=product_ids)


# ############################################################################
# Catalog (Inline View) Routes
# ############################################################################
@app.route('/catalog_inline_new/')
@requires_auth
def catalog_inline_new():
    sale_order = get_current_sale_order()

    category_ids = openerp.eshopCategory.search([
        ('type', '=', 'normal')])

    product_qty_dict = {}
    for line in sale_order.order_line:
        if line.product_id.id in product_qty_dict.keys():
            product_qty_dict[line.product_id.id] += line.product_uom_qty
        else:
            product_qty_dict[line.product_id.id] = line.product_uom_qty

    return render_template(
        'catalog_inline_new.html', category_ids=category_ids,
        product_qty_dict=product_qty_dict)


@app.route('/catalog_inline/')
@requires_auth
def catalog_inline():
    sale_order_id = get_current_sale_order_id()
    catalog_inline = openerp.productProduct.get_current_eshop_product_list(
        sale_order_id)

    labels = {}
    for product in catalog_inline:
        for lid in product['label_ids']:
            if lid in labels:
                continue
            write_date = openerp.productLabel.perm_read(lid)[0]['write_date']
            labels[lid] = hashlib.sha1(str(write_date)).hexdigest()

    return render_template(
        'catalog_inline.html',
        catalog_inline=catalog_inline,
        labels=labels,
    )


@app.route('/catalog_inline_quantity_update', methods=['POST'])
def catalog_inline_quantity_update():
    res = set_quantity(
        int(request.form['product_id']), request.form['new_quantity'], True,
        'set')
    if request.is_xhr:
        return jsonify(result=res)
    flash(res['message'], res['state'])
    return redirect_url_for('catalog_inline')


# ############################################################################
# Product Routes
# ############################################################################
@app.route('/product/<int:product_id>')
@requires_auth
def product(product_id):
    # Get Products
    product = get_openerp_object('product.product', product_id)

    # Get Parent Categories
    parent_categories = []
    parent = get_openerp_object('eshop.category', product.eshop_category_id)
    while parent:
        parent_categories.insert(0, {'id': parent.id, 'name': parent.name})
        parent = get_openerp_object('eshop.category', parent.parent_id)

    return render_template(
        'product.html', product_id=product_id,
        parent_categories=parent_categories)


@app.route("/product_popup/<int:product_id>")
@requires_auth
def product_popup(product_id):
    return render_template('product_popup.html', product_id=product_id)


@app.route("/product_image_popup/<int:product_id>")
@requires_auth
def product_image_popup(product_id):
    return render_template('product_image_popup.html', product_id=product_id)


@app.route("/product_add_qty/<int:product_id>", methods=['POST'])
@requires_auth
def product_add_qty(product_id):
    res = set_quantity(
        int(product_id), request.form['quantity'], True, 'add')
    flash(res['message'], res['state'])
    return redirect_url_for('product', product_id=product_id)
