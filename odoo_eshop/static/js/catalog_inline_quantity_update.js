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



$('.quantity').change(function(e){
    self = this;
    var new_quantity = e.currentTarget.value;
    var product_id = e.currentTarget.id.split('_')[1];
    
    $.ajax({
        url: FLASK_URL_FOR['catalog_inline_quantity_update'],
        type: "POST",
        data: {new_quantity: new_quantity, product_id: product_id},
        timeout: 1000,
    }).done(function(msg){
        if (msg.result.state == 'success' || msg.result.state == 'warning'){
            $('#quantity_' + product_id).val(msg.result.quantity);
            $('#quantity_' + product_id).toggleClass('not_null_qty', (msg.result.quantity != '0'));
            if (msg.result.amount_total == '0') {
                $('#nav_shopping_cart').css('visibility', 'hidden');
            }
            else {
                $('#nav_shopping_cart').css('visibility', 'visible');
                $('#nav_amount_total').replaceWith("<span id='nav_amount_total'>" + msg.result.amount_total + "</span>");

                if (msg.result.minimum_ok){
                    $('#nav_shopping_cart_ok').css('display', 'inline-block');
                    $('#nav_shopping_cart_warning').css('display', 'none');
                }
                else{
                    $('#nav_shopping_cart_ok').css('display', 'none');
                    $('#nav_shopping_cart_warning').css('display', 'inline-block');
                }
            }
        }
        if (msg.result.state != 'success') {
            $('.flashes').replaceWith("<div class='flashes'><p class='text-center bg-" + msg.result.state + "'>" + msg.result.message  + "</p></div>");
        }
        else {
            $('.flashes').replaceWith("<div class='flashes' />");
        }
    }).fail(function(xhr, textstatus){
        $('.flashes').replaceWith("<div class='flashes'><p class='text-center bg-danger'>" + AJAX_MESSAGE_ERROR + "</p></div>");
    });
});
