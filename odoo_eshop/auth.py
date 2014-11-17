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
from erp import openerp


def login(username, password):
    session['partner_login'] = username
    session['partner_password'] = password


def logout():
    session.clear()


def authenticate():
    return render_template('login.html')


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'partner_login' in session and 'partner_password' in session:
            partner = False

            try:
                # Partner Authentification
                partner_id = openerp.ResPartner.login(
                    session['partner_login'], session['partner_password'])
                if partner_id:
                    partner = openerp.ResPartner.browse(partner_id)
                else:
                    logout()
                    flash(_('Login/password incorrects'), 'danger')
                    return authenticate()
            except:
                logout()
                flash(_(
                    """Service Unavailable."""
                    """If you had a pending purchase, """
                    """You have not lost your Shopping Cart."""), 'danger')
                return authenticate()

            session['partner_id'] = partner.id
            session['partner_name'] = partner.name

            return f(*args, **kwargs)
        return authenticate()
    return decorated
