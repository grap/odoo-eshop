#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Extra Libs
from flask import request, render_template, flash, redirect, url_for, \
    jsonify

# Custom Tools
from eshop_app.application import app
from eshop_app.tools.erp import openerp
from eshop_app.tools.auth import requires_auth
from eshop_app.models.models import get_openerp_object
from eshop_app.models.obs_sale_order import change_product_qty, load_sale_order


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
@app.route('/catalog_inline/', defaults={'category_id': False})
@app.route("/catalog_inline/<int:category_id>")
@requires_auth
def catalog_inline(category_id):
    sale_order = load_sale_order()

    category_ids = openerp.eshopCategory.search([
        ('type', '=', 'normal')])

    product_qty_dict = {}
    for line in sale_order.order_line:
        if line.product_id.id in product_qty_dict.keys():
            product_qty_dict[line.product_id.id] += line.product_uom_qty
        else:
            product_qty_dict[line.product_id.id] = line.product_uom_qty

#    product_ids = openerp.ProductProduct.search([
#        ('eshop_state', '=', 'available')], order='eshop_category_id, name')
#    catalog_inline = openerp.saleOrder.get_current_eshop_product_list(
#        sale_order and sale_order.id or False)
    return render_template(
        'catalog_inline.html', category_ids=category_ids,
        product_qty_dict=product_qty_dict)


@app.route('/catalog_inline_quantity_update', methods=['POST'])
def catalog_inline_quantity_update():
    res = change_product_qty(
        request.form['new_quantity'], 'set',
        product_id=int(request.form['product_id']))
    if request.is_xhr:
        return jsonify(result=res)
    flash(res['message'], res['state'])
    return redirect(url_for('catalog_inline'))


# ############################################################################
# Product Routes
# ############################################################################
@app.route("/product/<int:product_id>")
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


@app.route("/product_add_qty/<int:product_id>", methods=['POST'])
@requires_auth
def product_add_qty(product_id):
    res = change_product_qty(
        request.form['quantity'], 'add', product_id=product_id)
    flash(res['message'], res['state'])
    return redirect(url_for('product', product_id=product_id))
