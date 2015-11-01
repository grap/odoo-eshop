#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Custom Tools
from eshop_app.tools.erp import openerp
from eshop_app.application import cache


# Private Consts
_MODELS = {
    'product.label': {
        'model': openerp.ProductLabel,
        'fields': ['name', 'code', 'image_small', 'image'],
    },
    'res.country': {
        'model': openerp.ResCountry,
        'fields': ['name'],
    },
    'res.country.department': {
        'model': openerp.ResCountryDepartment,
        'fields': ['name'],
    },
    'product.uom': {
        'model': openerp.ProductUom,
        'fields': ['name', 'eshop_description'],
    },
    'res.company': {
        'model': openerp.ResCompany,
        'fields': [
            'has_eshop', 'eshop_minimum_price', 'eshop_title', 'eshop_url',
            'eshop_facebook_url', 'eshop_twitter_url', 'eshop_google_plus_url',
            'eshop_home_text', 'eshop_home_image', 'eshop_image_small',
            'eshop_vat_included', 'eshop_register_allowed',
            'eshop_list_view_enabled',
            'manage_delivery_moment', 'manage_recovery_moment',
        ],
    },
}


# Public Section
@cache.memoize()
def get_openerp_object(model_name, id):
    if not id:
        return False
    myModel = _MODELS[model_name]
    myObj = _OpenerpModel(id)
    data = myModel['model'].browse(id)
    for key in myModel['fields']:
        setattr(myObj, key, getattr(data, key))
    return myObj


# Private Model
class _OpenerpModel(object):
    def __init__(self, id):
        self.id = id
