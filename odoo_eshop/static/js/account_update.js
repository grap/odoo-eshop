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

$('.account_data').change(function(e){
    self = this;
    $.ajax({
        url: FLASK_URL_FOR['account_update'],
        type: "POST",
        data: {
            new_phone: $('#account_phone').val(),
            new_mobile: $('#account_mobile').val(),
            new_street: $('#account_street').val(),
            new_street2: $('#account_street2').val(),
            new_zip: $('#account_zip').val(),
            new_city: $('#account_city').val(),
            }, timeout: 1000,
    }).done(function(msg){
        if (msg.result.state == 'success' || msg.result.state == 'warning'){
            $('#account_phone').val(msg.result.phone);
            $('#account_mobile').val(msg.result.mobile);
            $('#account_street').val(msg.result.street);
            $('#account_street2').val(msg.result.street2);
            $('#account_zip').val(msg.result.zip);
            $('#account_city').val(msg.result.city);
        }
        display_message(msg.result.state, msg.result.message, true);
    }).fail(function(xhr, textstatus){
        display_fail_message();
    });
});
