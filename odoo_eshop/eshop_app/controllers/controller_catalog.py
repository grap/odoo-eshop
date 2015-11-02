#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Extra Libs
from flask import render_template

# Custom Tools
from eshop_app.application import app
from eshop_app.tools.erp import openerp
from eshop_app.tools.auth import requires_auth


# ############################################################################
# Catalog (Tree View) Routes
# ############################################################################
@app.route('/catalog_tree/', defaults={'category_id': False})
@app.route("/catalog_tree/<int:category_id>")
@requires_auth
def catalog_tree(category_id):
    parent_categories = []
    current_category = False

    # Get Child Categories
    categories = openerp.eshopCategory.browse(
        [('parent_id', '=', category_id)])

    parent_categories = []
    # Get Parent Categories
    if category_id:
        current_category = openerp.eshopCategory.browse(category_id)
        # Get Parent Categories
        parent = current_category
        while parent:
            parent_categories.insert(
                0, {'id': parent.id, 'name': parent.name})
            parent = parent.parent_id

    # Get Products
    product_ids = openerp.ProductProduct.search([
        ('eshop_state', '=', 'available'),
        ('eshop_category_id', '=', category_id)], order='name')
    return render_template(
        'catalog_tree.html',
        categories=categories,
        parent_categories=parent_categories,
        current_category=current_category,
        product_ids=product_ids,
    )
