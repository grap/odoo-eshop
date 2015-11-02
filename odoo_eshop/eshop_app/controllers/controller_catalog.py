#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Extra Libs
from flask import render_template

# Custom Tools
from eshop_app.application import app
from eshop_app.tools.erp import openerp
from eshop_app.tools.auth import requires_auth
from eshop_app.models.models import get_openerp_object


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
    # Get Parent Categories
    if category_id:
        parent = get_openerp_object('eshop.category', category_id)
        # Get Parent Categories
        while parent:
            parent_categories.insert(
                0, {'id': parent.id, 'name': parent.name})
            parent = parent.parent_id

    return render_template(
        'catalog_tree.html',
        parent_categories=parent_categories,
        category_ids=category_ids,
        product_ids=product_ids,
    )
