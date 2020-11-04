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


def get_invoice_pdf(invoice_id):
    model_name, model_id = odoo.IrModelData.get_object_reference(
        'account', 'account_invoices'
    )
    report_datas = odoo.model(model_name).read(model_id)
    report_id = odoo.report(
        'account.report_invoice', [invoice_id], report_datas
    )
    done = False
    while not done:
        report = odoo.report_get(report_id)
        done = report['state']
    return base64.b64decode(report["result"])


def get_order_pdf(order_id):
    model_name, model_id = odoo.IrModelData.get_object_reference(
        'sale', 'report_sale_order'
    )
    report_datas = odoo.model(model_name).read(model_id)
    report_id = odoo.report(
        'grap_qweb_report.grap_template_sale_order', [order_id], report_datas
    )
    done = False
    while not done:
        report = odoo.report_get(report_id)
        done = report['state']
    return base64.b64decode(report["result"])
