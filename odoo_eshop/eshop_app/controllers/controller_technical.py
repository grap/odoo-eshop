#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Libs
import base64
import logging
from datetime import datetime  # , timedelta
import pytz

# Extra Libs
from flask import (
    request, render_template, flash, make_response, url_for, redirect)

from flask.ext.babel import gettext as _

# Custom Tools
from ..application import app
from ..application import cache
from ..application import babel

from ..tools.web import redirect_url_for
from ..tools.config import conf
from ..tools.auth import requires_connection, requires_auth
from ..tools.erp import openerp, tz

# Custom Models
from ..models.models import (
    get_openerp_object,
    invalidate_openerp_object,
    currency,
)

from ..models.res_partner import get_current_partner, get_current_partner_id
from ..models.res_company import get_current_company
from ..models.sale_order import get_current_sale_order, get_is_vat_included


# ############################################################################
# Home Route
# ############################################################################
@app.route("/")
@requires_connection
def home():
    if get_current_partner_id():
        return redirect_url_for('home_logged')
    return render_template('home.html')


@app.route("/home_logged.html")
@requires_auth
def home_logged():
    company = get_openerp_object(
        'res.company', int(conf.get('openerp', 'company_id')))
    if company.manage_recovery_moment\
            and not company.manage_delivery_moment:
        pending_moment_groups = openerp.SaleRecoveryMomentGroup.browse(
            [('state', 'in', 'pending_sale')])
        if len(pending_moment_groups) == 0:
            # Not possible to purchase for the time being
            futur_moment_groups = openerp.SaleRecoveryMomentGroup.browse(
                [('state', 'in', 'futur')])
            if len(futur_moment_groups) > 0:
                min_date = futur_moment_groups[0].min_sale_date
                for item in futur_moment_groups:
                    min_date = min(min_date, item.min_sale_date)
                flash(_(
                    "It is not possible to buy for the time being,"
                    " You can buy starting at %(day)s %(date)s %(time)s.",
                    day=to_day(min_date), date=to_date(min_date),
                    time=to_time(min_date)), 'warning')
            else:
                flash(_(
                    "It is not possible to buy for the time being,"
                    " but you can see the catalog in the meantime."),
                    'warning')
        elif len(pending_moment_groups) == 1:
            # Display end Date to order
            flash(_(
                "You can buy until %(day)s %(date)s %(time)s.",
                day=to_day(pending_moment_groups[0].max_sale_date),
                date=to_date(pending_moment_groups[0].max_sale_date),
                time=to_time(pending_moment_groups[0].max_sale_date)), 'info')
    elif company.manage_delivery_moment\
            and not company.manage_recovery_moment:
        partner = get_current_partner()
        if not partner.delivery_categ_id:
            flash(_(
                "Your account is not correctly set : your delivery group"
                " is not defined. Please contact your seller to fix the"
                " problem"), 'danger')
    else:
        flash(_('Recovery / Delivery Moment Unset'), 'danger')
    return render_template('home.html')


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
    print "get_image %s %s %s %s" % (model, id, field, sha1)
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
@app.route("/unavailable_service.html")
@requires_auth
def unavailable_service():
    return render_template('unavailable_service.html')


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

    def current_partner():
        return get_current_partner()

    def current_company():
        return get_current_company()

    def current_sale_order():
        return get_current_sale_order()

    def is_vat_included(company, sale_order, partner):
        return get_is_vat_included(company, sale_order, partner)

    return dict(
        get_object=get_object, current_partner=current_partner,
        current_company=current_company, current_sale_order=current_sale_order,
        is_vat_included=is_vat_included)


# ############################################################################
# Babel Local Selector
# ############################################################################
@babel.localeselector
def locale_selector():
    partner = get_current_partner()
    if partner:
        return partner.lang
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


@app.template_filter('surcharge_to_string')
def surcharge_to_string(value):
    if not value:
        return ''
    elif value > 0:
        # Display a Surcharge
        return '(+%s%%)' % float_to_string(value)
    else:
        # Display a discount
        return '(-%s%%)' % float_to_string(value)


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
