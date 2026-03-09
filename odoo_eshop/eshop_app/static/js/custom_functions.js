/******************************************************************************
    eShop for Odoo
    Copyright (C) 2015-Today GRAP (http://www.grap.coop)
    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
******************************************************************************/


function update_header(order_id, amount_total_header, minimum_ok){
    if (order_id == false) {
        $('#nav_shopping_cart').css('visibility', 'hidden');
    }
    else {
        $('#nav_shopping_cart').css('visibility', 'visible');
        $('#nav_amount_total').replaceWith("<span id='nav_amount_total'>" + amount_total_header + "</span>");

        if (minimum_ok){
            $('#nav_shopping_cart_ok').css('display', 'inline-block');
            $('#nav_shopping_cart_warning').css('display', 'none');
        }
        else{
            $('#nav_shopping_cart_ok').css('display', 'none');
            $('#nav_shopping_cart_warning').css('display', 'inline-block');
        }
    }
}

function display_message(state, message, always){
    if (state != 'success' || always) {
        $('.flashes').replaceWith("<div class='flashes'><p class='text-center bg-" + state + "'>" + message  + "</p></div>");
    }
    else {
        $('.flashes').replaceWith("<div class='flashes' />");
    }
}

function display_fail_message(){
    $('.flashes').replaceWith("<div class='flashes'><p class='text-center bg-danger'>" + AJAX_MESSAGE_ERROR + "</p></div>");
}

/* Variables globales */
let qtyUpdateTimer = null;

/* Adjust quantity by AJAX Call with python product_adjust_qty function */
function adjustQty(delta, product_id) {

    /* Get minimum and rounded qty */
    const product_min_qty_el = document.getElementById(`product-min-qty`);
    const product_min_qty = parseFloat(product_min_qty_el.innerHTML) || 1;

    const product_rounded_qty_el = document.getElementById(`product-rounded-qty`);
    const product_rounded_qty = parseFloat(product_rounded_qty_el.innerHTML) || 1;

    /* Get input */
    const input_el = document.getElementById(`quantityInput`);
    let input_qty = parseFloat(input_el.value) || 0;

    /* Calculate new quantity */
    let new_quantity = Math.max(input_qty + delta * product_rounded_qty, product_min_qty);

    /* Update immedialty input.. */
    input_el.value = new_quantity;
    clearTimeout(qtyUpdateTimer);

    /* .. but wait before sending value to cart */
    qtyUpdateTimer = setTimeout(function() {
        sendQtyToServer(new_quantity, product_id);
    }, 500); // 0.5sec
}

function sendQtyToServer(new_quantity, product_id) {

    currentAjaxCall = $.ajax({
        url: FLASK_URL_FOR['product_adjust_qty'],
        type: "POST",
        data: {new_quantity: new_quantity, product_id: product_id},
        timeout: AJAX_TIMEOUT
    }).done(function(msg){

        currentAjaxCall = false;

        if (msg.result.state == 'success' || msg.result.state == 'warning'){
            // Maj quantity input
            $('#quantityInput').val(msg.result.quantity);
            // Maj header total
            update_header(msg.result.order_id, msg.result.amount_total_header, msg.result.minimum_ok);
            display_message('success', msg.result.message, false);
        } else {
            alert(msg.message);
        }

    }).fail(function(){
        currentAjaxCall = false;
        display_fail_message();
    });
}

function deleteLine(product_id) {
    currentAjaxCall = $.ajax({
        url: FLASK_URL_FOR['product_adjust_qty'],
        type: "POST",
        data: {new_quantity: 0, product_id: product_id},
        timeout: AJAX_TIMEOUT
    }).done(function(msg){
        currentAjaxCall = false;

        if (msg.result.state == 'success' || msg.result.state == 'warning'){
            /*Maj quantity input*/
            $('#quantityInput').val(msg.result.quantity);
            /*Maj header total */
            update_header(msg.result.order_id, msg.result.amount_total_header, msg.result.minimum_ok);
            display_message('success', msg.result.message, false);
            /* reload page to have button "Add to cart" */
            location.reload();
        } else {
            alert(msg.message);
        }
    }).fail(function(xhr, textstatus){
        currentAjaxCall = false;
        display_fail_message();
    });
}

