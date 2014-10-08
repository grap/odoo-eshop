import base64

import erppeek

from config import conf


def init_openerp(url, login, password, database):
    openerp = erppeek.Client(url)
    uid = openerp.login(login, password=password, database=database)
    return openerp, uid


openerp, uid = init_openerp(
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
        'account.invoice', [invoice_id], report_datas
    )
    done = False
    while not done:
        report = openerp.report_get(report_id)
        done = report['state']
    return base64.b64decode(report["result"])
