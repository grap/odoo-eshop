#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Librairies
from functools import wraps
from flask import (
    session,
    render_template,
    flash,
)
from flask.ext.babel import gettext as _

# Custom Modules
from sale_order import load_sale_order
from erp import openerp


def login(username, password):
    session['partner_login'] = username
    session['partner_password'] = password


def logout():
    for k, v in session.items():
        del session[k]


def authenticate():
    return render_template('login.html')


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'partner_login' in session and 'partner_password' in session:
            uid = partner = False

            try:
                # Partner Authentification
                partner_id = openerp.ResPartner.login(
                    session['partner_login'], session['partner_password'])
                if partner_id:
                    partner = openerp.ResPartner.browse(partner_id)
            except:
                logout()
                flash(_('Login/password incorrects'), 'danger')
                return authenticate()

            session['user_id'] = uid
            session['partner_id'] = partner.id
            session['partner_name'] = partner.name

            # Load Data
            load_sale_order()
            return f(*args, **kwargs)
        return authenticate()
    return decorated
