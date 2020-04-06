#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Extra Libs
from flask import request, render_template, flash, jsonify
from flask.ext.babel import gettext as _

# Custom Tools
from ..application import app
from ..tools.web import redirect_url_for
from ..tools.auth import requires_auth
from ..models.tools import currency
from ..models.models import execute_odoo_command

from ..models.sale_order import (
    get_current_sale_order_lines,
    get_current_sale_order,
    set_quantity,
)

from ..models.res_partner import get_current_partner_id
from ..models.res_company import get_current_company


# ############################################################################
# Shopping Cart Management Routes
# ############################################################################
@app.route("/shopping_cart")
@requires_auth
def shopping_cart():
    order = get_current_sale_order()
    if not order:
        return redirect_url_for('home')
    sale_order_lines = get_current_sale_order_lines(order)
    return render_template(
        'shopping_cart.html',
        sale_order_lines=sale_order_lines)


@app.route('/shopping_cart_note_update', methods=['POST'])
def shopping_cart_note_update():
    note = execute_odoo_command(
        "sale.order",
        "eshop_set_note",
        get_current_partner_id(),
        request.form['note'],
    )
    result = {
        'state': 'success',
        'note': note,
        'message': _("Your comment has been successfully updated.")}
    if request.is_xhr:
        return jsonify(result=result)
    flash(result['message'], result['state'])
    return redirect_url_for('shopping_cart')


@app.route('/shopping_cart_quantity_update', methods=['POST'])
def shopping_cart_quantity_update():
    res = set_quantity(
        int(request.form['product_id']), request.form['new_quantity'], False,
        'set')
    if request.is_xhr:
        return jsonify(result=res)
    flash(res['message'], res['state'])
    return redirect_url_for('shopping_cart')


@app.route("/shopping_cart_delete")
@requires_auth
def shopping_cart_delete():
    execute_odoo_command(
        "sale.order",
        "eshop_delete_current_sale_order",
        get_current_partner_id(),
    )
    flash(_("Your shopping cart has been successfully deleted."), 'success')
    return redirect_url_for('home_logged')


@app.route("/shopping_cart_delete_line/<int:line_id>")
@requires_auth
def shopping_cart_delete_line(line_id):
    result = execute_odoo_command(
        "sale.order",
        "eshop_delete_sale_order_line",
        get_current_partner_id(),
        line_id,
    )
    if result == "line_deleted":
        flash(_("The Line has been successfully deleted."), 'success')
        return redirect_url_for('shopping_cart')
    else:
        flash(_("Your shopping cart has been deleted."), 'success')
        return redirect_url_for('home_logged')


# ############################################################################
# Recovery Moment Place Route
# ############################################################################
@app.route("/recovery_moment_place")
@requires_auth
def recovery_moment_place():
    company = get_current_company()
    recovery_moments = execute_odoo_command(
        "sale.recovery.moment", "browse",
        [('state', '=', 'pending_sale')],
        order="min_recovery_date"
    )
    sale_order = get_current_sale_order()
    if (company.eshop_minimum_price != 0
            and company.eshop_minimum_price > sale_order.amount_total):
        flash(
            _("You have not reached the ceiling : ") +
            currency(company.eshop_minimum_price),
            'warning')
        return redirect_url_for('shopping_cart')
    return render_template(
        'recovery_moment_place.html',
        recovery_moments=recovery_moments)


@app.route("/select_recovery_moment/<int:recovery_moment_id>")
@requires_auth
def select_recovery_moment(recovery_moment_id):
    result = execute_odoo_command(
        "sale.order",
        "eshop_select_recovery_moment",
        get_current_partner_id(),
        recovery_moment_id,
    )
    if result == "recovery_moment_complete":
        flash(_(
            "The recovery moment is complete."
            " Please try again."), 'error')
        return redirect_url_for('shopping_cart')
    else:
        flash(_("Your Sale Order is now confirmed."), 'success')
        return redirect_url_for('orders')
