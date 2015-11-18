#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Libs
import base64
import logging
from datetime import datetime  # , timedelta
import pytz

# Extra Libs
from flask import request, session, render_template, flash, make_response,\
    url_for, redirect

from flask.ext.babel import gettext as _

# Custom Tools
from ..application import app
from ..application import cache
from ..application import babel

from ..tools.config import conf
from ..tools.auth import requires_connection
from ..tools.erp import openerp, tz

# Custom Models
from ..models.models import get_openerp_object, \
    invalidate_openerp_object

from ..models.obs_sale_order import load_sale_order, currency


# ############################################################################
# image Routes
# ############################################################################
@app.route(
    "/get_image/<string:model>/<int:id>/<string:field>/<string:sha1>/")
@cache.cached(key_prefix='odoo_eshop/%s')
def get_image(model, id, field, sha1):
    """Return an image depending of
    @param model: Odoo model. Ex: 'product.product';
    @param id: Id of the object. Ex: 4235';
    @param field: Odoo field name. Ex: 'image_medium';
    @param sha1: unused param in the function. Used to force client
        to reload obsolete images.
    """
    openerp_model = {
        'product.product': openerp.ProductProduct,
        'eshop.category': openerp.eshopCategory,
        'product.delivery.category': openerp.ProductDeliveryCategory,
        'product.label': openerp.ProductLabel,
        'res.company': openerp.ResCompany,
    }[model]
    if not openerp_model:
        # Incorrect Call
        return render_template('404.html'), 404
    image_data = openerp_model.read(id, field)
    if not image_data:
        # No image found
        file_name = {
            'product.product': 'images/product_product_without_image.png',
            'eshop.category': 'images/eshop_category_without_image.png',
            'res.company': 'images/res_company_without_image.png',
        }[model]
        return redirect(url_for('static', filename=file_name))

    response = make_response(base64.decodestring(image_data))
    # TODO FIXME Ask Arthur how to manage cached dynamic datas
#    expiry_time = datetime.utcnow() + timedelta(days=30)
#    response.headers["Expires"] = \
#        expiry_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
#    response.headers['Last-Modified'] = "Fri, 23 Oct 2015 12:33:52 GMT"
#    response.headers['Cache-Control'] = 'max-age=300000000'
    response.headers['Content-Type'] = 'image/jpeg'
    return response


# ############################################################################
# Technical Routes
# ############################################################################
@app.route(
    "/invalidation_cache/" +
    "<string:key>/<string:model>/<int:id>/<string:fields_text>/")
@requires_connection
def invalidation_cache(key, model, id, fields_text):
    if key == conf.get('cache', 'invalidation_key'):
        # Invalidate Object cache
        invalidate_openerp_object(str(model), int(id))
        return render_template('200.html'), 200
    else:
        return render_template('404.html'), 404


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(Exception)
def error(e):
    flash(_(
        "An unexcepted error occured. Please try again in a while"), 'danger')
    logging.exception('an error occured')
    return render_template('500.html'), 500


# ############################################################################
# Context Processor
# ############################################################################
@app.context_processor
def utility_processor():
    def get_object(model_name, id):
        return get_openerp_object(model_name, id)

    def get_company():
        return get_openerp_object(
            'res.company', int(conf.get('openerp', 'company_id')))

    def get_current_sale_order():
        return load_sale_order()

    return dict(
        get_company=get_company, get_object=get_object,
        get_current_sale_order=get_current_sale_order)


# ############################################################################
# Babel Local Selector
# ############################################################################
@babel.localeselector
def locale_selector():
    if session.get('partner_id', False):
        try:
            partner = openerp.ResPartner.browse(session['partner_id'])
            return partner.lang
        except:
            pass
    return request.accept_languages.best_match(['fr', 'en'])


def get_local_date(str_utc_date, schema):
    """From UTC string Datetime, return local datetime"""
    mytz = pytz.timezone(tz)
    utc_date = datetime.strptime(str_utc_date, schema)
    return mytz.fromutc(utc_date)


# ############################################################################
# Template filters
# ############################################################################

@app.template_filter('to_currency')
def compute_currency(amount):
    return currency(amount)


@app.template_filter('float_to_string')
def float_to_string(value):
    if (value % 1) == 0:
        return str(int(value))
    else:
        return str(value).replace('.', ',')


@app.template_filter('function_to_eval')
def function_to_eval(arg):
    return arg


@app.template_filter('to_day')
def to_day(arg):
    if ' ' in arg:
        int_day = get_local_date(arg, '%Y-%m-%d %H:%M:%S').strftime('%w')
    else:
        int_day = get_local_date(arg, '%Y-%m-%d').strftime('%w')
    return {
        '0': _('Sunday'),
        '1': _('Monday'),
        '2': _('Tuesday'),
        '3': _('Wednesdsay'),
        '4': _('Thursday'),
        '5': _('Friday'),
        '6': _('Saturday'),
    }[int_day]


@app.template_filter('to_ids')
def to_ids(arg):
    return [x.id for x in arg]


@app.template_filter('to_date')
def to_date(arg):
    if ' ' in arg:
        return get_local_date(arg, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
    else:
        return get_local_date(arg, '%Y-%m-%d').strftime('%d/%m/%Y')


@app.template_filter('to_datetime')
def to_datetime(arg):
    return get_local_date(arg, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %Hh%M')


@app.template_filter('to_time')
def to_time(arg):
    return get_local_date(arg, '%Y-%m-%d %H:%M:%S').strftime('%Hh%M')


@app.template_filter('get_current_quantity')
def get_current_quantity(product_id):
    sale_order = load_sale_order()
    if sale_order:
        for line in sale_order.order_line:
            if line.product_id.id == product_id:
                return line.product_uom_qty
    return 0


# TODO FIXME: Problem with erpeek. Text of field selection unavaible
@app.template_filter('fresh_category')
def fresh_category(value):
    return {
        'extra': _('Extra'),
        '1': _('Category I'),
        '2': _('Category II'),
        '3': _('Category III'),
    }[value]


@app.template_filter('empty_if_null')
def empty_if_null(value):
    return value if value else ''
