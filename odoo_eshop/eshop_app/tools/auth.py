#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Lib
from config import conf

# Extra Lib
from functools import wraps
from flask import session, render_template, flash, redirect, url_for
from flask.ext.babel import gettext as _

# Custom Tools
from .erp import openerp


def login(username, password):
    session['partner_login'] = username
    session['partner_password'] = password


def logout():
    session.clear()


def _load_global_data_if_needed():
    # TODO: IMP. Set this information in "environment vars" and not
    # "session" vars.

    if not session.get('global_data_loaded', False):
        shop = openerp.SaleShop.browse(int(conf.get('openerp', 'shop_id')))
        session['global_data_loaded'] = True
        session['eshop_title'] = shop.eshop_title
        session['eshop_website_url'] = shop.eshop_website_url
        session['eshop_twitter_url'] = shop.eshop_twitter_url
        session['eshop_facebook_url'] = shop.eshop_facebook_url
        session['eshop_google_plus_url'] = shop.eshop_google_plus_url
        session['eshop_image_small'] = shop.eshop_image_small
        session['eshop_register_allowed'] = shop.eshop_register_allowed
        session['eshop_minimum_price'] = shop.eshop_minimum_price
        session['eshop_list_view_enabled'] = shop.eshop_list_view_enabled
        session['eshop_vat_included'] = shop.eshop_vat_included
        session['manage_recovery_moment'] = shop.manage_recovery_moment
        session['manage_delivery_moment'] = shop.manage_delivery_moment


# Decorator called for pages that DON'T require authentication
def requires_connection(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check OpenERP Connexion
        if not openerp:
            # Connexion Failed, redirect to unavailable service page
            flash(_(
                "Distant Service Unavailable. If you had a pending purchase,"
                " you have not lost your Shopping Cart."
                " Thank you connect again in a while."),
                'danger')
            return render_template('unavailable_service.html')
        else:
            # Connexion OK: Store in session some params and return asked page
            _load_global_data_if_needed()
            return f(*args, **kwargs)

    return decorated


# Decorator called for pages that requires authentication
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check OpenERP Connexion
        if not openerp:
            # Connexion Failed, redirect to unavailable service page
            flash(_(
                "Distant Service Unavailable. If you had a pending purchase,"
                " you have not lost your Shopping Cart."
                " Thank you connect again in a while."),
                'danger')
            return render_template('unavailable_service.html')
        else:
            # Connexion OK: Store in session some params
            _load_global_data_if_needed()

            # Check OpenERP Authentication
            if not session.get('partner_id', False):
                # User no authenticated
                return redirect(url_for('login_view'))
            else:
                return f(*args, **kwargs)

    return decorated
