from flask import request, render_template, flash, jsonify

from ..application import app
from ..tools.web import redirect_url_for
from ..tools.auth import requires_auth
from ..models.models import get_odoo_object, execute_odoo_command
from ..models.sale_order import set_quantity
from ..models.res_partner import get_current_partner_id


# ############################################################################
# Catalog (Tree View) Routes
# ############################################################################
@app.route('/catalog_tree/', defaults={'category_id': False})
@app.route("/catalog_tree/<int:category_id>")
@requires_auth
def catalog_tree(category_id):

    category_ids = execute_odoo_command(
        "eshop.category",
        "search",
        [('parent_id', '=', category_id)],
    )

    # Get Products
    product_ids = execute_odoo_command(
        "product.product",
        "search",
        [
            ('eshop_state', '=', 'available'),
            ('eshop_category_id', '=', category_id)
        ], order='name'
    )

    parent_categories = []
    parent = get_odoo_object('eshop.category', category_id)
    # Get Parent Categories
    while parent:
        parent_categories.insert(0, {'id': parent.id, 'name': parent.name})
        parent = get_odoo_object('eshop.category', parent.parent_id)

    return render_template(
        'catalog_tree.html', parent_categories=parent_categories,
        category_ids=category_ids, product_ids=product_ids)


# ############################################################################
# Catalog (Inline View) Routes
# ############################################################################
@app.route('/catalog_inline/')
@requires_auth
def catalog_inline():
    catalog_inline = execute_odoo_command(
        "product.product",
        "get_current_eshop_product_list",
        get_current_partner_id()
    )
    print(catalog_inline)
    return render_template(
        'catalog_inline.html',
        catalog_inline=catalog_inline,
    )


@app.route('/catalog_inline_quantity_update', methods=['POST'])
def catalog_inline_quantity_update():
    res = set_quantity(
        int(request.form['product_id']), request.form['new_quantity'], True,
        'set')
    if True:  # request.is_xhr:
        return jsonify(result=res)
    # TODO, fix me, the website is not working anymore if javascript is
    # disabled
    flash(res['message'], res['state'])
    return redirect_url_for('catalog_inline')


# ############################################################################
# Product Routes
# ############################################################################
@app.route('/product/<int:product_id>')
@requires_auth
def product(product_id):
    # Get Products
    product = get_odoo_object('product.product', product_id)

    # Get Parent Categories
    parent_categories = []
    parent = get_odoo_object('eshop.category', product.eshop_category_id)
    while parent:
        parent_categories.insert(0, {'id': parent.id, 'name': parent.name})
        parent = get_odoo_object('eshop.category', parent.parent_id)

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
