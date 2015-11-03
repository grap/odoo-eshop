#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Custom Tools
from eshop_app.tools.erp import openerp
from eshop_app.application import cache


# Private Consts
_ESHOP_OPENERP_MODELS = {
    'product.product': {
        'model': openerp.ProductProduct,
        'fields': [
            'id', 'name', 'uom_id', 'image', 'image_medium', 'list_price',
            'eshop_category_id', 'label_ids', 'eshop_minimum_qty',
            'eshop_rounded_qty', 'origin_description', 'maker_description',
            'fresh_category', 'description', 'country_id', 'department_id',
            'default_code', 'delivery_categ_id', 'eshop_taxes_description'],
    },
    'eshop.category': {
        'model': openerp.eshopCategory,
        'fields': [
            'id', 'name', 'available_product_qty', 'child_qty',
            'image_medium', 'type', 'parent_id', 'product_ids', 'complete_name'],
    },
    'product.delivery.category': {
        'model': openerp.ProductDeliveryCategory,
        'fields': ['id', 'name', 'image'],
    },
    'product.label': {
        'model': openerp.ProductLabel,
        'fields': ['id', 'name', 'code', 'image', 'image_small'],
    },
    'res.country': {
        'model': openerp.ResCountry,
        'fields': ['id', 'name'],
    },
    'res.country.department': {
        'model': openerp.ResCountryDepartment,
        'fields': ['id', 'name'],
    },
    'product.uom': {
        'model': openerp.ProductUom,
        'fields': ['id', 'name', 'eshop_description'],
    },
    'res.company': {
        'model': openerp.ResCompany,
        'fields': [
            'id', 'name', 'has_eshop', 'eshop_minimum_price', 'eshop_title',
            'eshop_url',
            'eshop_facebook_url', 'eshop_twitter_url', 'eshop_google_plus_url',
            'eshop_home_text', 'eshop_home_image', 'eshop_image_small',
            'eshop_vat_included', 'eshop_register_allowed',
            'eshop_list_view_enabled',
            'manage_delivery_moment', 'manage_recovery_moment',
        ],
    },
}


def get_openerp_object(model_name, id):
    if not id:
        return False
    res = _get_openerp_object(model_name, id)
    return res


# Public Section
@cache.memoize()
def _get_openerp_object(model_name, id):
    if not id:
        return False
    myModel = _ESHOP_OPENERP_MODELS[model_name]
    myObj = _OpenerpModel(id)
    data = myModel['model'].read(id, myModel['fields'])
    for key in myModel['fields']:
        if key[-3:] == '_id' and data[key]:
            setattr(myObj, key, data[key][0])
        else:
            setattr(myObj, key, data[key])
    return myObj


def invalidate_openerp_object(model_name, id):
    cache.delete_memoized(_get_openerp_object, model_name, id)


# Private Model
class _OpenerpModel(object):
    def __init__(self, id):
        self.id = id
