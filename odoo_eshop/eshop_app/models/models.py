# encoding: utf-8

# Standard Libs
import os
import base64
import logging
import shutil

# Custom Tools
from ..tools.erp import openerp
from ..application import cache


logger = logging.getLogger('odoo_eshop')


# ###########################
# Public Sectioon
# ###########################

def get_odoo_uncached_object(model_name, *args):
    odooModel = _ODOO_MODELS[model_name]['proxy']
    datas = execute_odoo_command_proxy(
        odooModel, "eshop_custom_load_data", *args)
    if datas:
        fields = datas[0].keys()

    result = []

    for data in datas:
        # Creating Object
        myObj = _OpenerpModel(model_name, data, fields)
        result.append(myObj)
    return result


def get_odoo_object(model_name, object_id, force_reload=False):
    """Load a data from odoo, for a given model and id.
    This will return a cached data or load the data from odoo.
    force_reload will delete cached data and for the reload of
    the data from Odoo.
    """
    if not object_id:
        return False
    if force_reload:
        _Memoize._set_cache(model_name, object_id, False)
    return _get_odoo_object(model_name, object_id)


def prefetch_all():
    """Prefetch all data from Odoo"""
    for model_name, setting in _ODOO_MODELS.iteritems():
        if setting.get("prefetch", False):
            objs = _load_from_odoo(model_name)
            for obj in objs:
                _Memoize._set_cache(model_name, obj.id, obj)


def execute_odoo_command(model_name, function, *_args, **_kwargs):
    odoo_proxy = _ODOO_MODELS[model_name]["proxy"]
    return execute_odoo_command_proxy(
        odoo_proxy, function, *_args, **_kwargs
    )


def execute_odoo_command_proxy(proxy, function, *_args, **_kwargs):
    return getattr(proxy, function)(*_args, **_kwargs)


# ###########################
# Private Sectioon
# ###########################
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
    },
    "sale.order": {
        "proxy": openerp.SaleOrder,
    },
    "sale.order.line": {
        "proxy": openerp.SaleOrderLine,
    },
    "sale.recovery.moment.group": {
        "proxy": openerp.SaleRecoveryMomentGroup,
    },
    "sale.recovery.moment": {
        "proxy": openerp.SaleRecoveryMoment,
    },
    "account.invoice": {
        "proxy": openerp.AccountInvoice,
    }
}


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


class _Memoize:

    def __init__(self, f):
        self.f = f

    def __call__(self, *args):
        result = cache.get(str(args))
        if not result:
            result = self.f(*args)
            cache.set(str(args), result)
        return result

    @classmethod
    def _set_cache(cls, model_name, object_id, value):
        args = (model_name, object_id)
        cache.set(str(args), value)


@_Memoize
def _get_odoo_object(model_name, object_id):
    objs = _load_from_odoo(model_name, [("id", "=", object_id)])
    if objs:
        return objs[0]
    else:
        return False


def _load_from_odoo(model_name, domain=False):
    odooModel = _ODOO_MODELS[model_name]['proxy']
    datas = execute_odoo_command_proxy(
        odooModel, "eshop_load_data", domain)

    if datas:
        fields = datas[0].keys()

    result = []

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
                image_data = execute_odoo_command_proxy(
                    odooModel, "read", myObj.id, [image_field]
                )[image_field]
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
        result.append(myObj)
    return result
