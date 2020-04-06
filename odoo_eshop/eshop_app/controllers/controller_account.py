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
from ..tools.erp import (
    get_invoice_pdf,
    get_order_pdf,
)

from ..tools.auth import logout, requires_connection, requires_auth

# Custom Models
from ..models.models import execute_odoo_command

from ..models.res_partner import (
    partner_domain,
    get_current_partner,
    get_current_partner_id,
    check_email,
    check_first_name,
    check_last_name,
    check_phone,
    check_password,
)

from ..models.res_company import get_current_company


# ############################################################################
# Account Route
# ############################################################################
@app.route("/account", methods=['GET', 'POST'])
@requires_auth
def account():

    incorrect_data = False
    vals = {}
    if not len(request.form) == 0:
        # Check Password
        if 'checkbox-change-password' in request.form:
            password, error_message = check_password(
                request.form['password_1'], request.form['password_2'])
            if error_message:
                incorrect_data = True
                flash(error_message, "danger")
            else:
                vals.update({"eshop_password": password})

        # Check Phone
        phone, error_message = check_phone(request.form['phone'])
        if error_message and phone:
            incorrect_data = True
            flash(error_message, "danger")

        # Check Phone
        mobile, error_message = check_phone(request.form['mobile'])
        if error_message and mobile:
            incorrect_data = True
            flash(error_message, "danger")

        if not incorrect_data:
            vals.update({
                    "street": request.form['street'],
                    "street2": request.form['street2'],
                    "zip": request.form['zip'],
                    "city": request.form['city'],
                    "phone": phone,
                    "mobile": mobile,
            })
            execute_odoo_command(
                "res.partner", "update_from_eshop",
                get_current_partner_id(), vals)
            flash(
                _("Account Datas updated successfully."),
                "success",
            )

    partner = get_current_partner(force_reload=True)
    return render_template('account.html', partner=partner)


# ############################################################################
# Orders Route
# ############################################################################
@app.route("/orders")
@requires_auth
def orders():
    orders = execute_odoo_command(
        "sale.order", "browse", [
            partner_domain('partner_id'),
            ('state', 'not in', ('draft', 'cancel')),
        ]
    )
    return render_template('orders.html', orders=orders)


@app.route('/order/<int:order_id>/download')
def order_download(order_id):
    order = execute_odoo_command("sale.order", "browse", order_id)
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
    invoices = execute_odoo_command(
        "account.invoice", "browse", [
            partner_domain('partner_id'),
            ('state', 'not in', ['draft', 'proforma', 'proforma2', 'cancel']),
        ]
    )
    return render_template('invoices.html', invoices=invoices)


@app.route('/invoices/<int:invoice_id>/download')
def invoice_download(invoice_id):
    invoice = execute_odoo_command(
        "account.invoice", "browse", invoice_id)
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
@app.route('/login.html/', defaults={'email': False}, methods=['GET', 'POST'])
@app.route("/login.html/<string:email>", methods=['GET', 'POST'])
@requires_connection
def login_view(email=False):
    if request.form.get('login', False):
        # Authentication asked
        partner_id = execute_odoo_command(
            "res.partner", "eshop_login",
            request.form['login'], request.form['password']
        )
        if partner_id:
            session['partner_id'] = partner_id
            return redirect_url_for('home_logged')
        else:
            flash(_('Login/password incorrects'), "danger")
    return render_template('login.html', email=email)


@app.route("/logout.html")
@requires_connection
def logout_view():
    logout()
    return redirect_url_for('home')


@app.route("/register.html", methods=['GET', 'POST'])
@requires_connection
def register():
    # Check if the operation is possible
    company = get_current_company()
    if not company.eshop_register_allowed or get_current_partner():
        return redirect_url_for('home')

    if len(request.form) == 0:
        return render_template('register.html')

    incorrect_data = False
    # Check First Name
    first_name, error_message = check_first_name(
        request.form["first_name"])
    if error_message:
        incorrect_data = True
        flash(error_message, "danger")

    # Check Last Name
    last_name, error_message = check_last_name(
        request.form["last_name"])
    if error_message:
        incorrect_data = True
        flash(error_message, "danger")

    # Check email
    email, error_message = check_email(request.form.get('email', False))
    if error_message:
        incorrect_data = True
        flash(error_message, "danger")
    elif email:
        partner_ids = execute_odoo_command(
            "res.partner", "search", [('email', '=', email)])
        if len(partner_ids) > 1:
            incorrect_data = True
            flash(_(
                "The '%(email)s' field is already used."
                "Please ask your seller to fix the problem.",
                email=email), "danger")
        elif len(partner_ids) == 1:
            incorrect_data = True
            partner = execute_odoo_command(
                "res.partner", "browse", partner_ids)[0]
            if partner.eshop_state == "enabled":
                flash(_(
                    "The '%(email)s' field is already associated to an"
                    " active account. Please click 'Recover Password',"
                    " if your forgot your credentials.", email=email),
                    "danger")
            elif partner.eshop_state == 'email_to_confirm':
                flash(_(
                    "The '%(email)s' field is already associated to an"
                    " account. Please finish the process to create an"
                    " account, by clicking on the link you received "
                    " by email.", email=email), "danger")
            else:
                flash(_(
                    "The '%(email)s' field is already associated to an"
                    " inactive account. Please ask your seller to activate"
                    " your account.", email=email), "danger")

    # Check Phone
    phone, error_message = check_phone(request.form['phone'])
    if error_message and phone:
        incorrect_data = True
        flash(error_message, "danger")

    # Check Mobile
    mobile, error_message = check_phone(request.form['mobile'])
    if error_message and mobile:
        incorrect_data = True
        flash(error_message, "danger")

    # Check password
    password, error_message = check_password(
        request.form['password_1'], request.form['password_2'])
    if error_message:
        incorrect_data = True
        flash(error_message, "danger")

    if not incorrect_data:
        # Registration is over
        execute_odoo_command(
            "res.partner", "create_from_eshop", {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "street": request.form['street'],
                "street2": request.form['street2'],
                "zip": request.form['zip'],
                "city": request.form['city'],
                "phone": phone,
                "mobile": mobile,
                "eshop_password": password,
            }
        )
        flash(_(
            "The registration is complete. Please check your mail box"
            " '%(email)s' and click on the link you received to activate"
            " your account.", email=email),
            "success")
        return render_template('home.html')
    else:
        return render_template('register.html')


@app.route("/activate_account/<int:id>/<string:email>", methods=['GET'])
@requires_connection
def activate_account(id, email):
    result = execute_odoo_command(
        "res.partner", "eshop_email_confirm", id, email)
    if result == "partner_not_found":
        flash(_("The validation process failed."), "danger")
        return redirect_url_for('home')

    if result == "bad_email":
        flash(_("Your email was not found."), "danger")
        return redirect_url_for('home')

    if result == "still_confirmed":
        flash(_("Your account is already enabled."), 'warning')
        return redirect_url_for('login_view')

    if result == "enabled":
        flash(_(
            "The validation process is over.\n"
            " You can now log in to begin to purchase."), 'success')
        return redirect_url_for('login_view')

    flash(_(
        "The validation process failed because your account"
        " is disabled. Please ask your seller to fix"
        " the problem."), 'danger')
    return redirect_url_for('home')


@app.route("/password_lost.html", methods=['GET', 'POST'])
@requires_connection
def password_lost():
    # Check if the operation is possible
    if get_current_partner():
        return redirect_url_for('home')

    if len(request.form) == 0:
        return render_template('password_lost.html')

    email = request.form.get('login', False)
    if not email:
        flash(_("'Email' Field is required"), "danger")
        return render_template('password_lost.html')

    result = execute_odoo_command(
        "res.partner", "eshop_password_lost", email)

    if result == "too_many_email":
        flash(_(
            "There is a problem with your account."
            " Please contact your seller."), "danger")
    elif result == "credential_maybe_sent":
        flash(_(
            " we sent an email to this mailbox, if this email was"
            " linked to an active account."), 'success')
    return redirect_url_for('login_view', email=email)
