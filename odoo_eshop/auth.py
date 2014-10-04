#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from functools import wraps

import erppeek

from flask import (
    g,
    session,
    render_template,
    flash,
)

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
            openerp = erppeek.Client(
                conf.get('openerp', 'url'),
            )
            # User Authentification
            uid = openerp.login(
                conf.get('auth', 'user_login'),
                password=conf.get('auth', 'user_password'),
                database=conf.get('openerp', 'database'),
            )
            # Partner Authentification
            partner = openerp.ResPartner.browse(
                [int(session['partner_login'])])
            if not (uid and partner):
                logout()
                flash(u'Login/password incorrects', 'danger')
                return authenticate()
            session['user_id'] = uid
            session['partner_id'] = partner[0].id
            session['partner_name'] = partner[0].name
            g.openerp = openerp

            # Load Data
            load_sale_order()
            return f(*args, **kwargs)
        return authenticate()
    return decorated
