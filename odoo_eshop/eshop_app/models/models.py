# encoding: utf-8

# Standard Libs
import os
import base64
import logging
import shutil

# Custom Tools
# from ..tools.config import conf
from ..tools.erp import openerp
from ..application import cache, app


logger = logging.getLogger('odoo_eshop')

_ODOO_MODELS = {
    'account.tax': {
        'proxy': openerp.AccountTax,
        'prefetch': True,
    },
    'eshop.category': {
        'proxy': openerp.eshopCategory,
        'prefetch': True,
        'image_fields': ['image', 'image_medium', 'image_small'],
    },
    'product.label': {
        'proxy': openerp.ProductLabel,
        'prefetch': True,
        'image_fields': ['image', 'image_small'],
    },
    'product.product': {
        'proxy': openerp.ProductProduct,
        'prefetch': True,
        'image_fields': ['image', 'image_medium', 'image_small'],
    },
    'product.uom': {
        'proxy': openerp.ProductUom,
        'prefetch': True,
    },
    'res.company': {
        'proxy': openerp.ResCompany,
        'prefetch': True,
        'image_fields': ['eshop_image_small']
    },
    'res.country': {
        'proxy': openerp.ResCountry,
        'prefetch': True,
    },
    'res.country.department': {
        'proxy': openerp.ResCountryDepartment,
        'prefetch': True,
    },
    'res.partner': {
        'proxy': openerp.ResPartner,
        'prefetch': True,
    }
}


# Global var that will be used as cache, after first load of the data
def get_current_prefetched_object():
    return CURRENT_PREFETCHED_OBJECT


def set_current_prefetched_object(prefetched_object):
    global CURRENT_PREFETCHED_OBJECT
    CURRENT_PREFETCHED_OBJECT = prefetched_object


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


@cache.memoize()
def _get_openerp_object(model_name, object_id):
    if not object_id:
        return False
    obj = get_current_prefetched_object()
    if obj:
        if obj.id == object_id and obj._name == model_name:
            return obj

    # # load the data
    _prefetch_objects(model_name, [('id', '=', object_id)])
    return get_current_prefetched_object()


def _prefetch_objects(model_name, domain=False):
    app.logger.info("Prefetching %s. domain : %s" % (model_name, domain or ''))
    odooModel = _ODOO_MODELS[model_name]['proxy']
    datas = odooModel.eshop_load_data(domain)

    if datas:
        fields = datas[0].keys()

    for data in datas:
        # Creating Object
        myObj = _OpenerpModel(model_name, data, fields)

        for image_field in _ODOO_MODELS[model_name].get('image_fields', []):

            local_path = "odoo_data/%s__%s__%d__%s" % (
                model_name.replace('.', '_'),
                image_field, myObj.id, myObj.image_write_date_hash)
            file_path = "./odoo_eshop/eshop_app/static/%s" % (local_path)

            setattr(myObj, "%s_local_path" % image_field, local_path)

            if os.path.isfile(file_path):
                continue
            else:
                # Load Data if exist
                image_data = odooModel.read(
                    myObj.id, [image_field])[image_field]
                if image_data:
                    file_object = open(file_path, "w")
                    file_object.write(base64.decodestring(image_data))
                    file_object.close()
                else:
                    # TODO copy
                    default_file_path =\
                        "./odoo_eshop/eshop_app/static/"\
                        "images/%s_without_image.png" % (
                            model_name.replace('.', '_'))
                    shutil.copy(default_file_path, file_path)
                    # local_path = 'images/%s_without_image.png' % (
                    # model_name.replace('.', '_'))
                    pass

        set_current_prefetched_object(myObj)

        # Call for memoize
        _get_openerp_object(model_name, myObj.id)


# Private Model
class _OpenerpModel(object):
    def __init__(self, model_name, data, fields):
        self.id = data['id']
        self._name = model_name
        for key in fields:
            if key[-3:] == '_id' and data[key]:
                setattr(self, key, data[key][0])
            else:
                setattr(self, key, data[key])


def prefetch():
    # Prefetch eShop Categories
    for model_name, setting in _ODOO_MODELS.iteritems():
        if setting['prefetch']:
            _prefetch_objects(model_name)
