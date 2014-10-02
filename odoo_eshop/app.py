#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from flask import Flask, g, request, redirect, session, url_for, \
    render_template
from config import conf
from auth import login, logout, requires_auth

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
    return redirect(url_for('hello'))


@app.route("/")
@requires_auth
def hello():
    sale_orders = g.openerp.SaleOrder.browse(
        [partner_domain()])
    return render_template(
        'home.html', sale_orders=sale_orders
    )


@app.route("/invoices.html")
@requires_auth
def invoices():
    account_invoices = g.openerp.AccountInvoice.browse(
        [partner_domain()])
    return render_template(
        'invoices.html', account_invoices=account_invoices
    )
