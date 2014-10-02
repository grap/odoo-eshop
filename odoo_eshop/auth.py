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
    session['openerp_user'] = username
    session['openerp_password'] = password


def logout():
    if 'openerp_user' in session:
        del session['openerp_user']
    if 'openerp_password' in session:
        del session['openerp_password']


def authenticate():
    return render_template('login.html')


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'openerp_user' in session and 'openerp_password' in session:
            openerp = erppeek.Client(
                conf.get('openerp', 'url'),
            )
            loggedin = openerp.login(
                session['openerp_user'],
                password=session['openerp_password'],
                database=conf.get('openerp', 'db'),
            )
            if not loggedin:
                logout()
                flash(u'Login/password incorrects', 'danger')
                return authenticate()
            g.openerp = openerp
            return f(*args, **kwargs)
        return authenticate()
    return decorated
