from functools import wraps

from flask import flash, render_template, session
from flask_babel import gettext as _

from .erp import odoo
from .web import redirect_url_for


def logout():
    session.clear()


# Decorator called for pages that DON'T require authentication
def requires_connection(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check OpenERP Connexion
        if not odoo:
            # Connexion Failed, redirect to unavailable service page
            flash(
                _(
                    "Distant Service Unavailable. If you had a pending purchase,"
                    " you have not lost your Shopping Cart."
                    " Thank you connect again in a while."
                ),
                "danger",
            )
            return render_template("unavailable_service.html")
        else:
            # Connexion OK: return asked page
            return f(*args, **kwargs)

    return decorated


# Decorator called for pages that requires authentication
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check OpenERP Connexion
        if not odoo:
            # Connexion Failed, redirect to unavailable service page
            flash(
                _(
                    "Distant Service Unavailable. If you had a pending purchase,"
                    " you have not lost your Shopping Cart."
                    " Thank you connect again in a while."
                ),
                "danger",
            )
            return render_template("unavailable_service.html")
        else:
            # Check OpenERP Authentication
            if not session.get("partner_id", False):
                # User no authenticated
                return redirect_url_for("login_view")
            else:
                return f(*args, **kwargs)

    return decorated
