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

$(document).ready(function() {
    $("input:text").focus(function() { $(this).select(); } );
});

var currentAjaxCall = false;

function GoToThePage(html_link) {
    var path = html_link.attributes.page_url.nodeValue;
    console.log("I'm going to go to " + path);
    if (currentAjaxCall) {
        // Wait for it
        console.log("WAITING")
        currentAjaxCall.then(function(){
            console.log("... OK!");
            window.location.href = path;
        });
    }
    else {
        console.log("DIRECTLY")
        window.location.href = path;
    }
};
