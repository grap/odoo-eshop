#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from flask import Flask, g, request, redirect, session, url_for, \
    render_template, flash
from config import conf
from auth import login, logout, requires_auth
from sale_order import add_product

app = Flask(__name__)
app.secret_key = conf.get('flask', 'secret_key')
app.debug = conf.get('flask', 'debug') == 'True'


def partner_domain():
    if 'partner_id' in session:
        return ('partner_id', '=', session['partner_id'])
    else:
        return ('partner_id', '=', -1)


# Auth Route
@app.route("/login.html", methods=['POST'])
def login_view():
    login(request.form['login'], request.form['password'])
    return redirect(request.args['return_to'])


@app.route("/logout.html")
def logout_view():
    logout()
    return redirect(url_for('home'))


@app.route("/")
@requires_auth
def home():
    return render_template(
        'home.html'
    )


@app.route("/invoices")
@requires_auth
def invoices():
    account_invoices = g.openerp.AccountInvoice.browse(
        [partner_domain()])
    return render_template(
        'invoices.html', account_invoices=account_invoices
    )


@app.route("/shopping_cart")
@requires_auth
def shopping_cart():
    sale_order = g.openerp.SaleOrder.browse(session['sale_order_id'])
    return render_template(
        'shopping_cart.html',
        sale_order=sale_order,
    )


@app.route("/product/<int:product_id>", methods=['GET', 'POST'])
@requires_auth
def product(product_id):
    # Get Products
    product = g.openerp.ProductProduct.browse(product_id)

    # Add product to shopping cart if wanted
    if request.method == 'POST':
        try:
            quantity = float(
                request.form['quantity'].replace(',', '.').strip())
        except ValueError:
            quantity = False
            flash(u'Invalid Quantity', 'error')
        if quantity:
            add_product(product, quantity)

    # Get Parent Categories
    parent_categories = []
    parent = product.eshop_category_id
    while parent:
        parent_categories.insert(0, {'id': parent.id, 'name': parent.name})
        parent = parent.parent_id

    return render_template(
        'product.html', product=product,
        parent_categories=parent_categories,
    )


@app.route('/catalog/', defaults={'category_id': False})
@app.route("/catalog/<int:category_id>")
@requires_auth
def catalog(category_id):
    parent_categories = []
    current_category = False

    # Get Child Categories
    categories = g.openerp.eshopCategory.browse(
        [('parent_id', '=', category_id)])

    parent_categories = []
    # Get Parent Categories
    if category_id:
        current_category = g.openerp.eshopCategory.browse(category_id)
        # Get Parent Categories
        parent = current_category
        while parent:
            parent_categories.insert(
                0, {'id': parent.id, 'name': parent.name})
            parent = parent.parent_id

    # Get Products
    products = g.openerp.ProductProduct.browse(
        [('eshop_ok', '=', True), ('eshop_category_id', '=', category_id)],
        order='name')
    return render_template(
        'catalog.html',
        categories=categories,
        parent_categories=parent_categories,
        current_category=current_category,
        products=products,
    )
