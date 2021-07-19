import odoorpc

from .config import conf


def init_odoo(host, port, login, password, database):
    odoo = odoorpc.ODOO(host, 'jsonrpc', port)
    db_list = odoo.json('/web/database/list', {})["result"]
    db_list.sort(reverse=True)

    if database not in db_list:
        # If the exact database is not found,
        # me make a fuzzy search. It makes the eshop working
        # on test servers, with database like
        # 'company_name_production__xx_xx_xx'

        for db in db_list:
            if db.startswith(database):
                database = db
                break

    if database not in db_list:
        raise Exception(
            ("Database %s not found. (fuzzy search failed)" % database)
        )
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
