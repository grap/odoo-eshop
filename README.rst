==========
Odoo Eshop
==========

.. |badge1| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1|

This app is a Flask Website that communicate with Odoo, to provide
a light eShop.


Main Features
-------------

- 100% responsive for mobile usage
- Compatible with differents payments method :
  - Pay on site
  - Using Customer Wallet : https://github.com/coopiteasy/addons/tree/16.0/customer_wallet
  - Paying online with Mollie : https://github.com/mollie/mollie-odoo/tree/16.0/payment_mollie_official

- Handle account (not a res user in Odoo database) 
- Two views to order :
    - kanban view, group by "eshop categories", that can be public without account
    - quick list view, that is searchable
- Handle order on a cart (cart = sale order on Odoo)
- Selecting a date and place to retrieve its orders
- See old orders and invoices
- See / change customer data.

Technical caracteristics
------------------------

- Do not host database, datas are requested on the fly to the odoo instance.
- Use Jinja as a template language (http://jinja.pocoo.org/docs/2.10/)


Installation for development
============================

Eshop Part
----------

```
git clone https://github.com/grap/odoo-eshop -b 16.0
cd odoo-eshop && ./install.sh
```

Odoo Installation
-----------------
    
This version is compatible with an Odoo 16.0 with the following module
installed ``sale_eshop`` available here : https://github.com/grap/grap-odoo-business


Configuration
-------------

in the config.ini file of the eshop, set the :

* ``[odoo] url`` : the url (and the port) of your odoo instance
* ``[odoo] database`` : the database name you want to connect
* ``[odoo] company_id`` : the odoo company ID want to connect

* ``[auth] user_login`` : the login of the eshop User
* ``[auth] user_password`` : the password of the eshop User


Launch eshop
------------

``./env/bin/python -m odoo_eshop``

Installation on server
======================

TODO
----

How to install on server : code, pip install, config, nginx, service


Create service
--------------

Create file in ``/etc/systemd/system/yourEshopName.service``

```
[Unit]
Description=yourEshopName eShop Daemon
After=network.target

[Service]
Type=simple
User=yourEshopUserOnConfig
Group=yourEshopUserOnConfig
ExecStart=/path/to/odoo_eshop.systemctl.sh


[Install]
WantedBy=multi-user.target
```  

Launch
------

``sudo systemctl status yourEshopName.service``


Journal
-------

``sudo journalctl -fu yourEshopName.service``


Credits
=======

Contributors
------------

* Sylvain LE GAL
* Quentin DUPONT

Do not contact contributors directly about support or help with technical issues.


Funders
-------

The development of this module has been financially supported by:

* GRAP, Groupement Régional Alimentaire de Proximité (https://www.grap.coop)
* Hashbang (https://hashbang.fr)
