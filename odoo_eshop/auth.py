#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Librairies
from functools import wraps
import erppeek
from flask import (
    g,
    session,
    render_template,
    flash,
)
from flask.ext.babel import gettext as _

# Custom Modules
from config import conf
from sale_order import load_sale_order


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
            openerp = erppeek.Client(
                conf.get('openerp', 'url'),
            )
            # User Authentification
            try:
                uid = openerp.login(
                    conf.get('auth', 'user_login'),
                    password=conf.get('auth', 'user_password'),
                    database=conf.get('openerp', 'database'),
                )
            except:
                flash(_('eShop is not available for the time being'), 'danger')
                return authenticate()

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
            g.openerp = openerp

            # Load Data
            load_sale_order()
            return f(*args, **kwargs)
        return authenticate()
    return decorated
