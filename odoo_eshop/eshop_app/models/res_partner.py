import re
import phonenumbers

from flask import session
from flask_babel import gettext as _

from .models import get_odoo_object

# https://stackoverflow.com/questions/8022530/
# how-to-check-for-valid-email-address#comment9819795_8022584
_RE_EMAIL = r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$"


def get_current_partner_id():
    return session.get('partner_id', False)


def get_current_partner(force_reload=False):
    return get_odoo_object(
        "res.partner",
        get_current_partner_id(),
        force_reload=force_reload,
    )


def partner_domain(partner_field):
    return (partner_field, '=', session.get('partner_id', -1))


def check_password(password_1, password_2):
    error_message = False
    if password_1 != password_2:
        # Check consistencies
        error_message = _("The 'Password' Fields do not match.")
    elif len(password_1) < 6 or re.search(r"\d", password_1) is None:
        error_message = _(
            "The password should have 6 characters or more,"
            " and should contain at least one digits.")
    return password_1, error_message


def check_first_name(txt_name):
    error_message = False
    txt_name = txt_name.strip()
    if not txt_name:
        error_message = _("'%s' is not a valid First Name." % txt_name)
    return txt_name, error_message


def check_last_name(txt_name):
    error_message = False
    txt_name = txt_name.strip()
    if not txt_name:
        error_message = _("'%s' is not a valid Last Name." % txt_name)
    return txt_name, error_message


def check_email(txt_email):
    txt_email = txt_email.strip()
    error_message = False
    if not re.search(_RE_EMAIL, txt_email):
        error_message = _("'%s' is not a valid email." % txt_email)
    return txt_email, error_message


def check_phone(txt_phone):
    iso_locale = "FR"
    error_message = False
    if re.search('[a-zA-Z]+', txt_phone):
        error_message = _(
            "'%(phone)s' is not a valid phone number."
            "It contains caracters.",
            phone=txt_phone)
        return txt_phone, error_message

    try:
        txt_phone = phonenumbers.format_number(
            phonenumbers.parse(txt_phone, iso_locale),
            phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except phonenumbers.phonenumberutil.NumberParseException:
        error_message = _(
            "'%(phone)s' is not a valid phone number.",
            phone=txt_phone)
    finally:
        return txt_phone, error_message
