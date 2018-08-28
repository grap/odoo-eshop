#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Libs
import datetime
import hashlib
import logging

# Custom Tools
from ..tools.erp import openerp
from ..application import cache, app


logger = logging.getLogger('odoo_eshop')


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
                    data['fields'].append('write_date')
            # allways load 'id' fields
            data['fields'].append('id')
            # If there are image, we manage write date
            data['manage_write_date'] = manage_write_date
            data['proxy'] = {
                'product.product': openerp.ProductProduct,
                'eshop.category': openerp.eshopCategory,
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


_PREFETCH_OBJECTS = {}

@cache.memoize()
def _get_openerp_object(model_name, id):
    if not id:
        return False
    myObj = _PREFETCH_OBJECTS.get('%s,%d' % (model_name, id), False)
    if myObj:
        return myObj
    myObj = _OpenerpModel(id)
    myModel = _get_openerp_models()[model_name]

    data = myModel['proxy'].read(id, myModel['fields'])
    for key in myModel['fields']:
        if key[-3:] == '_id' and data[key]:
            setattr(myObj, key, data[key][0])
        elif key =='write_date':
            setattr(myObj, 'sha1', hashlib.sha1(str(data[key])).hexdigest())
        else:
            setattr(myObj, key, data[key])
    return myObj

def _prefetch_objects(model_name, domain):
    print "_prefetch_objects %s" % model_name
    logger.info("Prefetching %s" % (model_name))
    global _PREFETCH_OBJECTS
    myModel = _get_openerp_models()[model_name]
    ids = myModel['proxy'].search(domain)
    datas = myModel['proxy'].read(ids, myModel['fields'])

    for data in datas:
        id = data['id']
        # Creating Object
        myObj = _OpenerpModel(id)
        # Adding regular values
        for key in myModel['fields']:
            if key[-3:] == '_id' and data[key]:
                setattr(myObj, key, data[key][0])
            elif key =='write_date':
                setattr(
                    myObj, 'sha1', hashlib.sha1(str(data[key])).hexdigest())
            else:
                setattr(myObj, key, data[key])
        _PREFETCH_OBJECTS['%s,%d' % (model_name, id)] = myObj

        # Call for memoize
        _get_openerp_object(model_name, id)
    _PREFETCH_OBJECTS = {}

# Private Model
class _OpenerpModel(object):
    def __init__(self, id):
        self.id = id

def prefetch():
    # Prefetch eShop Categories
    _prefetch_objects('eshop.category', [])
    _prefetch_objects('product.label', [])
    _prefetch_objects('product.uom', [('eshop_description', '!=', False)])
    _prefetch_objects('res.country', [])
    _prefetch_objects('res.country.department', [])
    _prefetch_objects('account.tax', [])

@cache.cached(key_prefix='odoo_eshop/%s')
def get_image_model(model, id, field, sha1):
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
        'product.label': openerp.ProductLabel,
        'res.company': openerp.ResCompany,
    }[model]

    image_data = openerp_model.read(id, field)
    if not image_data:
        return False
    else:
        return image_data
