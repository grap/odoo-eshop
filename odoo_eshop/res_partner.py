#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import re
import phonenumbers
from flask import session
from erp import openerp, uid
from flask.ext.babel import gettext as _


def sanitize_phone(txt_phone, iso_locale):
    if re.search('[a-zA-Z]+', txt_phone):
        return {
            'state': 'danger',
            'message': _(
                "'%(phone)s' is not a valid phone number."
                "It contains caracters.",
                phone=txt_phone)}
    try:
        res = phonenumbers.format_number(
            phonenumbers.parse(txt_phone, iso_locale),
            phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return res
    except phonenumbers.phonenumberutil.NumberParseException:
        return {
            'state': 'danger',
            'message': _(
                "'%(phone)s' is not a valid phone number.",
                phone=txt_phone)}


def change_res_partner(
        partner_id, phone, mobile, street, street2, zip, city):
    # Sanityze phone value
    phone = sanitize_phone(phone, 'FR') if phone else ''
    if type(phone) is dict:
        return phone

    # Sanityze mobile value
    mobile = sanitize_phone(mobile, 'FR') if mobile else ''
    if type(mobile) is dict:
        return mobile

    openerp.ResPartner.write([partner_id], {
        'phone': phone,
        'mobile': mobile,
        'street': street,
        'street2': street2,
        'zip': zip,
        'city': city,
    })
    res = {
        'state': 'success',
        'phone': phone,
        'mobile': mobile,
        'street': street,
        'street2': street2,
        'zip': zip,
        'city': city,
        'message': _(
            """Account Datas updated successfully.""")}
    return res

