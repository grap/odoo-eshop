from ..models.models import get_odoo_object

# ############################################################################
# I/O Odoo - Payment Transaction
# ############################################################################
def get_transaction_status(transaction_id):
    res = get_odoo_object("payment.transaction", transaction_id)
    if res:
        return res.state
    else:
        return False

def get_transaction(transaction_id):
    result = get_odoo_object("payment.transaction", transaction_id)
    result = result or []
    return result
