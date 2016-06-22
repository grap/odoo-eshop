#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Lib
import io

# Extra Libs
from flask import request, render_template, flash, session, abort, send_file


from flask.ext.babel import gettext as _

# Custom Tools
from ..application import app

from ..tools.web import redirect_url_for
from ..tools.config import conf
from ..tools.erp import openerp, get_invoice_pdf, get_order_pdf
from ..tools.auth import logout, requires_connection, requires_auth


# Custom Models
from ..models.models import get_openerp_object

from ..models.res_partner import (
    partner_domain,
    change_res_partner,
    get_current_partner,
    sanitize_email,
    check_password,
)


# ############################################################################
# Account Route
# ############################################################################
@app.route("/account", methods=['GET', 'POST'])
@requires_auth
def account():
    partner = get_current_partner()

    if not len(request.form) == 0:
        new_password = False
        if 'checkbox-change-password' in request.form:
            password_ok = check_password(
                request.form['password_1'], request.form['password_2'])
            if password_ok:
                new_password = request.form['password_1']
                flash(_("Password changed successfully"), 'success')

        res = change_res_partner(
            partner.id,
            request.form['phone'],
            request.form['mobile'],
            request.form['street'],
            request.form['street2'],
            request.form['zip'],
            request.form['city'],
            new_password)
        flash(res['message'], res['state'])

    return render_template('account.html', partner=partner)


# ############################################################################
# Orders Route
# ############################################################################
@app.route("/orders")
@requires_auth
def orders():
    orders = openerp.SaleOrder.browse([
        partner_domain('partner_id'),
        ('state', 'not in', ('draft', 'cancel'))])
    return render_template('orders.html', orders=orders)


@app.route('/order/<int:order_id>/download')
def order_download(order_id):
    order = openerp.SaleOrder.browse(order_id)
    partner = get_current_partner()
    # Manage Access Rules
    if not order or order.partner_id.id != partner.id:
        return abort(404)

    content = get_order_pdf(order_id)
    filename = "%s_%s.pdf" % (_('order'), order.name.replace('/', '_'))
    return send_file(
        io.BytesIO(content),
        as_attachment=True,
        attachment_filename=filename,
        mimetype='application/pdf'
    )


# ############################################################################
# Invoices Route
# ############################################################################
@app.route("/invoices")
@requires_auth
def invoices():
    invoices = openerp.AccountInvoice.browse([
        partner_domain('partner_id'),
        ('state', 'not in', ('draft', 'proforma', 'proforma2', 'cancel'))])
    return render_template('invoices.html', invoices=invoices)


@app.route('/invoices/<int:invoice_id>/download')
def invoice_download(invoice_id):
    invoice = openerp.AccountInvoice.browse(invoice_id)
    partner = get_current_partner()
    if not invoice or invoice.partner_id.id != partner.id:
        return abort(404)

    content = get_invoice_pdf(invoice_id)
    filename = "%s_%s.pdf" % (_('invoice'), invoice.number.replace('/', '_'))
    return send_file(
        io.BytesIO(content),
        as_attachment=True,
        attachment_filename=filename,
        mimetype='application/pdf'
    )


# ############################################################################
# Auth Route
# ############################################################################
@app.route("/login.html", methods=['GET', 'POST'])
@requires_connection
def login_view():
    if request.form.get('login', False):
        # Authentication asked
        partner_id = openerp.ResPartner.login(
            request.form['login'], request.form['password'])
        if partner_id:
            session['partner_id'] = partner_id
            return redirect_url_for('home_logged')
        else:
            flash(_('Login/password incorrects'), 'danger')
    return render_template('login.html')


@app.route("/logout.html")
@requires_connection
def logout_view():
    logout()
    return redirect_url_for('home')


@app.route("/register.html", methods=['GET', 'POST'])
@requires_connection
def register():
    # Check if the operation is possible
    company = get_openerp_object(
        'res.company', int(conf.get('openerp', 'company_id')))
    if not company.eshop_register_allowed or get_current_partner():
        return redirect_url_for('home')

#    previous_captcha = session.get('captcha', False)
#    PATH_TTF = conf.get('captcha', 'font_path').split(',')
#    image = ImageCaptcha(fonts=PATH_TTF)

#    new_captcha = str(randint(0,999999)).replace('1', '3').replace('7', '4')
#    captcha_data = base64.b64encode(image.generate(new_captcha).getvalue())
#    session['captcha'] = new_captcha

    captcha_data = False

    if len(request.form) == 0:
        pass
#        session['captcha_ok'] = False
    else:
        # TODO refactor in a extra file or in Odoo
        complete_data = mail_ok = password_ok = True
        # Check captcha
#        if not session.get('captcha_ok', False) and\
#                request.form.get('captcha', False) != previous_captcha:
#            flash(
#                _("The 'captcha' field is not correct. Please try again"),
#                'danger')
#            return render_template(
#                'register.html', captcha_data=captcha_data)
#        else:
#            session['captcha_ok'] = True

        email = sanitize_email(request.form.get('email', False))
        if email:
            # Check email in Database (inactive account)
            partner_ids = openerp.ResPartner.search([
                ('email', '=', email)])
            if len(partner_ids) > 1:
                mail_ok = False
                flash(_(
                    "The '%(email)s' field is already used."
                    "Please ask your seller to fix the problem.",
                    email=email), 'danger')
            elif len(partner_ids) == 1:
                mail_ok = False
                partner = openerp.ResPartner.browse(partner_ids)[0]
                if partner.eshop_active:
                    flash(_(
                        "The '%(email)s' field is already associated to an"
                        " active account. Please click 'Recover Password',"
                        " if your forgot your credentials.", email=email),
                        'danger')
                elif partner.eshop_state == 'email_to_confirm':
                    flash(_(
                        "The '%(email)s' field is already associated to an"
                        " account. Please finish the process to create an"
                        " account, by clicking on the link you received "
                        " by email.", email=email), 'danger')
                else:
                    flash(_(
                        "The '%(email)s' field is already associated to an"
                        " inactive account. Please ask your seller to activate"
                        " your account.", email=email), 'danger')

        if not mail_ok:
            return render_template('register.html')

        password_ok = check_password(
            request.form['password_1'], request.form['password_2'])

        if complete_data and mail_ok and password_ok:
            # Registration is over
            openerp.ResPartner.create_from_eshop({
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'email': request.form['email'],
                'street': request.form['street'],
                'street2': request.form['street2'],
                'zip': request.form['zip'],
                'city': request.form['city'],
                'eshop_password': request.form['password_1'],
            })
            flash(_(
                "The registration is complete. Please check your mail box"
                " '%(email)s' and click on the link you received to activate"
                " your account.",
                email=request.form['email']), 'success')
            return redirect_url_for('home')
        else:
            return render_template('register.html')

    return render_template('register.html', captcha_data=captcha_data)


@app.route("/activate_account/<int:id>/<string:email>", methods=['GET'])
@requires_connection
def activate_account(id, email):
    partner = openerp.ResPartner.browse([id])[0]
    if not partner or partner.email != email:
        flash(_("The validation process failed."), 'danger')
    elif partner.eshop_state in ['first_purchase', 'enabled']:
        flash(_("Your account is already enabled."), 'warning')
    elif partner.eshop_state in ['email_to_confirm']:
        openerp.ResPartner.write([partner.id], {
            'eshop_state': 'first_purchase'})
        flash(_(
            "The validation process is over.\n"
            " You can now log in to begin to purchase."), 'success')
    else:
        flash(_(
            "The validation process failed because your account is disabled."
            " Please ask your seller to fix the problem."), 'warning')
    return redirect_url_for('home')


@app.route("/password_lost.html", methods=['GET', 'POST'])
@requires_connection
def password_lost():
    # Check if the operation is possible
    if get_current_partner():
        return redirect_url_for('home')
#    previous_captcha = session.get('captcha', False)
#    PATH_TTF = conf.get('captcha', 'font_path').split(',')
#    image = ImageCaptcha(fonts=PATH_TTF)

#    new_captcha = str(randint(0,999999)).replace('1', '3').replace('7', '4')
#    captcha_data = base64.b64encode(image.generate(new_captcha).getvalue())
#    session['captcha'] = new_captcha

    captcha_data = False

    if len(request.form) == 0:
        pass
#        session['captcha_ok'] = False
    else:
        # Check captcha
        # if request.form.get('captcha', False) != previous_captcha:
        #    flash(
        #        _("The 'captcha' field is not correct. Please try again"),
        #        'danger')
        #    return render_template(
        #        'password_lost.html', captcha_data=captcha_data)

        email = sanitize_email(request.form.get('login', False))
        if not email:
                flash(_("'Email' Field is required"), 'danger')
                return render_template(
                    'password_lost.html')
        else:
            partner_ids = openerp.ResPartner.search([
                ('email', '=', email)])
            if len(partner_ids) > 1:
                flash(_(
                    "There is a problem with your account."
                    " Please contact your seller."), 'danger')
                return redirect_url_for('home')
            else:
                if len(partner_ids) == 1:
                    openerp.ResPartner.send_credentials(partner_ids)
                flash(_(
                    " we sent an email to this mailbox, if this email was"
                    " linked to an active account."), 'success')
                return redirect_url_for('home')

    return render_template('password_lost.html', captcha_data=captcha_data)
