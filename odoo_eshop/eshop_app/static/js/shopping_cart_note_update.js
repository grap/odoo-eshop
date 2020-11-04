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

$('#shopping_cart_note').change(function(e){
    self = this;
    console.log("calling AJAX");
    console.log(currentAjaxCall);
    currentAjaxCall = $.ajax({
        url: FLASK_URL_FOR['shopping_cart_note_update'],
        type: "POST",
        data: {
            note: $('#shopping_cart_note').val(),
            },
        timeout: AJAX_TIMEOUT,
    }).done(function(msg){
        currentAjaxCall = false;
        console.log("HAVE THE ANSWER. OK");
        if (msg.result.state == 'success' || msg.result.state == 'warning'){
            $('#shopping_cart_note').val(msg.result.note);
        }
        display_message(msg.result.state, msg.result.message, true);
    }).fail(function(xhr, textstatus){
        currentAjaxCall = false;
        console.log("HAVE THE ANSWER. KO");
        display_fail_message();
    });
});
