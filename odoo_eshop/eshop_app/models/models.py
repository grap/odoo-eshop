#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Libs
import hashlib

# Custom Tools
from ..tools.erp import openerp
from ..application import cache, app


# Tools Function
def currency(n):
    if not n:
        n = 0
    return ('%.02f' % n).replace('.', ',') + u' €'


# Public Section
def invalidate_openerp_object(model_name, id):
    cache.delete_memoized(_get_openerp_object, model_name, id)


def get_openerp_object(model_name, id):
    if not id:
        return False
    res = _get_openerp_object(model_name, id)
    return res


# Private Section
def _get_openerp_models():
    if hasattr(app, '_eshop_openerp_models'):
        _eshop_openerp_models = getattr(app, '_eshop_openerp_models')
    else:
        # Load Model
        _eshop_openerp_models = openerp.ResCompany.GetEshopModel()
        for model, data in _eshop_openerp_models.iteritems():
            manage_write_date = False
            for field in data['fields']:
                if 'image' in field:
                    manage_write_date = True
                    data['fields'].remove(field)
            # allways load 'id' fields
            data['fields'].append('id')
            # If there are image, we manage write date
            data['manage_write_date'] = manage_write_date
            data['proxy'] = {
                'product.product': openerp.ProductProduct,
                'eshop.category': openerp.eshopCategory,
                'product.delivery.category': openerp.ProductDeliveryCategory,
                'product.label': openerp.ProductLabel,
                'res.country': openerp.ResCountry,
                'res.country.department': openerp.ResCountryDepartment,
                'product.uom': openerp.ProductUom,
                'res.company': openerp.ResCompany,
                'res.partner': openerp.ResPartner,
                'account.tax': openerp.AccountTax,
            }[model]
            # we set model
        setattr(app, '_eshop_openerp_models', _eshop_openerp_models)
    return _eshop_openerp_models


@cache.memoize()
def _get_openerp_object(model_name, id):
    if not id:
        return False
    myModel = _get_openerp_models()[model_name]
    myObj = _OpenerpModel(id)
    data = myModel['proxy'].read(id, myModel['fields'])
    if myModel['manage_write_date']:
        write_date = myModel['proxy'].perm_read(id)[0]['write_date']
        setattr(myObj, 'sha1', hashlib.sha1(str(write_date)).hexdigest())
    for key in myModel['fields']:
        if key[-3:] == '_id' and data[key]:
            setattr(myObj, key, data[key][0])
        else:
            setattr(myObj, key, data[key])
    return myObj


# Private Model
class _OpenerpModel(object):
    def __init__(self, id):
        self.id = id
