#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Librairies
from config import conf
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


def home():
    try:
        shop = openerp.SaleShop.browse(int(conf.get('openerp', 'shop_id')))
        eshop_home_text=shop.eshop_home_text
        eshop_image=shop.eshop_image
        session['eshop_image_small']=shop.eshop_image_small
        eshop_register_allowed = shop.eshop_register_allowed
    except:
        # This exception is fully ignored because we have to display
        # an home page, eventually with flashed messages that mention problems
        eshop_register_allowed = eshop_home_text = eshop_image = False
        flash(_(
            "Distant Service Unavailable. If you had a pending purchase,"
            " you have not lost your Shopping Cart."
            " Thank you connect again in a while."),
            'danger')
        return unavailable_service()
    return render_template(
        'home.html', eshop_home_text=eshop_home_text, eshop_image=eshop_image,
        eshop_register_allowed=eshop_register_allowed)


def authenticate():
    return render_template('login.html')


def unavailable_service():
    return render_template('unavailable_service.html')


def requires_connection(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not openerp:
            flash(_(
                "Distant Service Unavailable. If you had a pending purchase,"
                " you have not lost your Shopping Cart."
                " Thank you connect again in a while."),
                'danger')
            return unavailable_service()
        else:
            return f(*args, **kwargs)
    return decorated


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
                if openerp:
                    flash(_(
                        "Local Service Unavailable. If you had a pending"
                        " purchase, you have not lost your Shopping"
                        " Cart. Thank you connect again in a while."),
                        'danger')
                else:
                    flash(_(
                        "Distant Service Unavailable. If you had a pending"
                        " purchase, you have not lost your Shopping"
                        " Cart. Thank you connect again in a while."),
                        'danger')
                return unavailable_service()

            session['partner_id'] = partner.id
            session['partner_name'] = partner.name

            # Store in session some settings
            shop = openerp.SaleShop.browse(int(conf.get('openerp', 'shop_id')))
            session['eshop_minimum_price'] = shop.eshop_minimum_price
            session['eshop_register_allowed'] = shop.eshop_register_allowed
            session['eshop_vat_included'] = shop.eshop_vat_included
            session['manage_delivery_moment'] = shop.manage_delivery_moment
            session['manage_recovery_moment'] = shop.manage_recovery_moment
            session['eshop_image_small'] = shop.eshop_image_small

            return f(*args, **kwargs)
        return home()
    return decorated
