#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Extra Libs
from flask import request, render_template, flash, jsonify
from flask.ext.babel import gettext as _

# Custom Tools
from ..application import app
from ..tools.web import redirect_url_for
from ..tools.config import conf
from ..tools.erp import openerp
from ..tools.auth import requires_auth
from ..models.models import (
    get_openerp_object,
    currency,
)

from ..models.sale_order import (
    change_sale_order_note,
    get_current_sale_order,
    get_current_sale_order_id,
    delete_current_sale_order,
    delete_sale_order_line,
    set_quantity,
)


# ############################################################################
# Shopping Cart Management Routes
# ############################################################################
@app.route("/shopping_cart")
@requires_auth
def shopping_cart():
    if not get_current_sale_order_id():
        return redirect_url_for('home')
    return render_template('shopping_cart.html')


@app.route('/shopping_cart_note_update', methods=['POST'])
def shopping_cart_note_update():
    res = change_sale_order_note(request.form['note'])
    if request.is_xhr:
        return jsonify(result=res)
    flash(res['message'], res['state'])
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
    delete_current_sale_order()
    flash(_("Your shopping cart has been successfully deleted."), 'success')
    return redirect_url_for('home_logged')


@app.route("/shopping_cart_delete_line/<int:line_id>")
@requires_auth
def shopping_cart_delete_line(line_id):
    delete_sale_order_line(line_id)
    if get_current_sale_order_id():
        flash(_("The Line has been successfully deleted."), 'success')
    else:
        flash(_("Your shopping cart has been deleted."), 'success')

    return shopping_cart()


# ############################################################################
# Recovery Moment Place Route
# ############################################################################
@app.route("/recovery_moment_place")
@requires_auth
def recovery_moment_place():
    company = get_openerp_object(
        'res.company', int(conf.get('openerp', 'company_id')))
    recovery_moments = openerp.SaleRecoveryMoment.browse(
        [('state', '=', 'pending_sale')], order="min_recovery_date")
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
    sale_order_id = get_current_sale_order_id()
    recovery_moment = openerp.SaleRecoveryMoment.browse(
        recovery_moment_id)
    # Todo Check if the moment is complete
    if recovery_moment.is_complete:
        flash(_(
            "The recovery moment is complete."
            " Please try again."), 'error')
        return redirect_url_for('shopping_cart')

    else:
        openerp.SaleOrder.write([sale_order_id], {
            'recovery_moment_id': recovery_moment_id,
        })
        openerp.SaleOrder.eshop_set_as_sent([sale_order_id])
        flash(_("Your Sale Order is now confirmed."), 'success')
        return redirect_url_for('orders')
