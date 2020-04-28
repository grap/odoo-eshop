# encoding: utf-8

# Standard Lib
import base64

# Extra Lib
import erppeek

# Custom Tools
from .config import conf


def init_openerp(url, login, password, database):
    try:
        openerp = erppeek.Client(url)
        uid = openerp.login(login, password=password, database=database)
        user = openerp.ResUsers.browse(uid)
        tz = user.tz
        return openerp, uid, tz
    except Exception:
        return False, False, False


openerp, uid, tz = init_openerp(
    conf.get('openerp', 'url'),
    conf.get('auth', 'user_login'),
    conf.get('auth', 'user_password'),
    conf.get('openerp', 'database'),
)


def get_invoice_pdf(invoice_id):
    model_name, model_id = openerp.IrModelData.get_object_reference(
        'account', 'account_invoices'
    )
    report_datas = openerp.model(model_name).read(model_id)
    report_id = openerp.report(
        'account.report_invoice', [invoice_id], report_datas
    )
    done = False
    while not done:
        report = openerp.report_get(report_id)
        done = report['state']
    return base64.b64decode(report["result"])


def get_order_pdf(order_id):
    model_name, model_id = openerp.IrModelData.get_object_reference(
        'sale', 'report_sale_order'
    )
    report_datas = openerp.model(model_name).read(model_id)
    report_id = openerp.report(
        'grap_qweb_report.grap_template_sale_order', [order_id], report_datas
    )
    done = False
    while not done:
        report = openerp.report_get(report_id)
        done = report['state']
    return base64.b64decode(report["result"])
