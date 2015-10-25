#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import re
import phonenumbers
from flask import session
from erp import openerp, uid
from flask.ext.babel import gettext as _

def password_check_quality(password):
    """
    From : http://stackoverflow.com/questions/16709638/
        checking-the-strength-of-a-password-how-to-check-conditions
    Copyright : http://stackoverflow.com/users/3856785/epi27231423
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        6 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 6

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # overall result
    password_ok = not (
        length_error or digit_error or uppercase_error or lowercase_error)

    return {
        'password_ok' : password_ok,
        'length_error' : length_error,
        'digit_error' : digit_error,
        'uppercase_error' : uppercase_error,
        'lowercase_error' : lowercase_error,
    }

def sanitize_email(txt_email):
    # TODO
    return txt_email

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
        partner_id, phone, mobile, street, street2, zip, city, password):
    # Sanitize phone value
    phone = sanitize_phone(phone, 'FR') if phone else ''
    if type(phone) is dict:
        return phone

    # Sanitize mobile value
    mobile = sanitize_phone(mobile, 'FR') if mobile else ''
    if type(mobile) is dict:
        return mobile

    vals = {
        'phone': phone,
        'mobile': mobile,
        'street': street,
        'street2': street2,
        'zip': zip,
        'city': city,
    }
    if password:
        vals['eshop_password'] = password

    openerp.ResPartner.write([partner_id], vals)
    res = {
        'state': 'success',
        'message': _("Account Datas updated successfully.")}
    return res

