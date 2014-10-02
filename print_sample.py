import base64
import erppeek


openerp = erppeek.Client()
invoice_id = 1

report_datas = openerp.execute(
    'account.invoice', 'invoice_print', [invoice_id]
)
report_id = openerp.report(
    'account.invoice', [invoice_id], report_datas
)
report = openerp.report_get(report_id)

with open('invoice-%d.pdf' % invoice_id, 'w') as invoice_pdf:
    invoice_pdf.write(base64.b64decode(report["result"]))
