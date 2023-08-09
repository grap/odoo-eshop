from ..tools.config import conf
from .models import get_odoo_object


def get_current_company(force_reload=False):
    return get_odoo_object(
        "res.company", int(conf.get("odoo", "company_id")), force_reload=force_reload
    )
