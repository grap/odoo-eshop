# encoding: utf-8

from ..tools.config import conf

from .models import get_openerp_object


def get_current_company():
    company_id = int(conf.get('openerp', 'company_id'))
    return get_openerp_object('res.company', company_id)
