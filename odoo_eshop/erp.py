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
