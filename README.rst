==========
Odoo Eshop
==========

.. |badge1| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1|

This app is a Flask Website that communicate with Odoo, to provide
a light eShop...

Installation
============

Eshop Part
----------

``
git clone https://github.com/grap/odoo-eshop -b 12.0
cd odoo-eshop && ./install.sh
``

Odoo Installation
-----------------

This version is compatible with an Odoo 12.0 with the following module
installed ``sale_eshop`` available here : https://github.com/grap/grap-odoo-business


Configuration
=============

in the config.ini file of the eshop, set the :

* ``[odoo] url`` : the url (and the port) of your odoo instance
* ``[odoo] database`` : the database name you want to connect
* ``[odoo] company_id`` : the odoo company ID want to connect

* ``[auth] user_login`` : the login of the eshop User
* ``[auth] user_password`` : the password of the eshop User



Main Features
-------------

Customer can:

- log in / log out
- see products in a kanban view, group by "eshop categories"
- see products in a list view
- create a sale order
- confirm sale order, selecting a date / a place
- see old orders
- see old invoices
- see / change his data.

Technical caracteristics
------------------------

- Do not host database, datas are requested on the fly to the odoo instance.
- Use Jinja as a template language (http://jinja.pocoo.org/docs/2.10/)

Initial eShop Settings
----------------------


Launch eshop
------------

``./env/bin/python -m odoo_eshop``

Credits
=======

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)

Do not contact contributors directly about support or help with technical issues.

Funders
-------

The development of this module has been financially supported by:

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)
* Hashbang (https://hashbang.fr)
