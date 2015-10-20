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

function update_header(amount_total, minimum_ok){
    if (amount_total == '0') {
        $('#nav_shopping_cart').css('visibility', 'hidden');
    }
    else {
        $('#nav_shopping_cart').css('visibility', 'visible');
        $('#nav_amount_total').replaceWith("<span id='nav_amount_total'>" + amount_total + "</span>");

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
