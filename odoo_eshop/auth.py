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


def login(username, password):
    session['partner_login'] = username
    session['partner_password'] = password


def logout():
    if 'partner_name' in session:
        del session['partner_name']
    if 'partner_login' in session:
        del session['partner_login']
    if 'partner_password' in session:
        del session['partner_password']


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
            session['partner_id'] = partner[0].id
            session['partner_name'] = partner[0].name
            g.openerp = openerp
            return f(*args, **kwargs)
        return authenticate()
    return decorated
