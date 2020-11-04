import base64

import odoorpc

from .config import conf


def init_odoo(host, port, login, password, database):
    odoo = odoorpc.ODOO(host, 'jsonrpc', port)
    uid = odoo.login(database, login, password)
    user = odoo.env['res.users'].browse(uid)
    tz = user.tz
    return odoo, uid, tz


odoo, uid, tz = init_odoo(
    conf.get('odoo', 'host'),
    conf.get('odoo', 'port'),
    conf.get('auth', 'user_login'),
    conf.get('auth', 'user_password'),
    conf.get('odoo', 'database'),
)
