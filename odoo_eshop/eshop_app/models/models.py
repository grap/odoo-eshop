import os
import base64
import logging
import shutil

from ..tools.erp import odoo
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
        myObj = _OdooModel(model_name, data, fields)
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
    for model_name, setting in _ODOO_MODELS.items():
        if setting.get("prefetch", False):
            objs = _load_from_odoo(model_name)
            for obj in objs:
                _Memoize._set_cache(model_name, obj.id, obj)


def execute_odoo_command(model_name, function, *_args, **_kwargs):
    odoo_proxy = _ODOO_MODELS[model_name]["proxy"]
    if function != "browse_by_search":
        return execute_odoo_command_proxy(
            odoo_proxy, function, *_args, **_kwargs
        )
    ids = execute_odoo_command_proxy(
            odoo_proxy, "search", *_args, **_kwargs
        )
    if ids:
        return execute_odoo_command_proxy(
            odoo_proxy, "browse", ids
        )
    return []


def execute_odoo_command_proxy(proxy, function, *_args, **_kwargs):
    return getattr(proxy, function)(*_args, **_kwargs)


# ###########################
# Private Section
# ###########################
_ODOO_MODELS = {
    'account.tax': {
        'proxy': odoo.env['account.tax'],
        'prefetch': True,
    },
    'eshop.category': {
        'proxy': odoo.env['eshop.category'],
        'prefetch': True,
        'image_fields': ['image', 'image_medium', 'image_small'],
    },
    'product.label': {
        'proxy': odoo.env['product.label'],
        'prefetch': True,
        'image_fields': ['image', 'image_medium', 'image_small'],
    },
    'product.product': {
        'proxy': odoo.env['product.product'],
        'prefetch': True,
        'image_fields': ['image', 'image_medium', 'image_small'],
    },
    'uom.uom': {
        'proxy': odoo.env['uom.uom'],
        'prefetch': True,
    },
    'res.company': {
        'proxy': odoo.env['res.company'],
        'prefetch': True,
        'image_fields': ['eshop_image_small']
    },
    'res.country': {
        'proxy': odoo.env['res.country'],
        'prefetch': True,
    },
    'res.country.state': {
        'proxy': odoo.env['res.country.state'],
        'prefetch': True,
    },
    'res.country.department': {
        'proxy': odoo.env['res.country.department'],
        'prefetch': True,
    },
    'res.partner': {
        'proxy': odoo.env['res.partner'],
        'prefetch': True,
    },
    "sale.order": {
        "proxy": odoo.env['sale.order'],
    },
    "sale.order.line": {
        "proxy": odoo.env['sale.order.line'],
    },
    "sale.recovery.moment.group": {
        "proxy": odoo.env['sale.recovery.moment.group'],
    },
    "sale.recovery.moment": {
        "proxy": odoo.env['sale.recovery.moment'],
    },
    "account.invoice": {
        "proxy": odoo.env['account.invoice'],
    }
}


# Private Model
class _OdooModel(object):
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
        myObj = _OdooModel(model_name, data, fields)

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
                )[0][image_field]
                if image_data:
                    file_object = open(file_path, "wb")
                    file_object.write(base64.b64decode(image_data))
                    file_object.close()
                else:
                    # TODO copy
                    default_file_path =\
                        "./odoo_eshop/eshop_app/static/"\
                        "images/%s_without_image.png" % (
                            model_name.replace('.', '_'))
                    shutil.copy(default_file_path, file_path)
                    pass
        result.append(myObj)
    return result
