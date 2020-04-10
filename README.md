.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==========
Odoo Eshop
==========

This app is a Flask Website that communicate with Odoo, to provide
a light eShop.

Installation
============

```
git clone https://github.com/grap/odoo-eshop
cd odoo-eshop && ./install.sh
```


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


Installation
============

Odoo Installation
-----------------

This version is compatible with an Odoo  8.0 with the following modules
installed ``sale_eshop`` available here : https://github.com/grap/odoo-addons-misc


Initial eShop Settings
----------------------

in the config.ini file of the eshop, set the :
* ``[openerp] url`` : the url (and the port) of your odoo instance
* ``[openerp] database`` : the database name you want to connect
* ``[openerp] company_id`` : the odoo company ID want to connect

* ``[auth] user_login`` : the login of the eshop User
* ``[auth] user_password`` : the password of the eshop User

Launch eshop
------------

```
./env/bin/python -m odoo_eshop
```


Roadmap / Know Issues
=====================

* controller_technical.py
    * the image url return a file to download, rather than a picture to display
    * IMPORTANT : it's always a 200 code, but should be 304 to light the
    server load + reduce transfert

* the server generate a lot of errors IOError

```
127.0.0.1 - - [06/Apr/2020 14:21:41] "GET /static/css/eshop_2.css HTTP/1.1" 200 -
Error on request:
Traceback (most recent call last):
  File "/home/sylvain/grap_dev/odoo-eshop-8.0/env/lib/python2.7/site-packages/werkzeug/serving.py", line 267, in run_wsgi
    execute(self.server.app)
  File "/home/sylvain/grap_dev/odoo-eshop-8.0/env/lib/python2.7/site-packages/werkzeug/serving.py", line 258, in execute
    write(data)
  File "/home/sylvain/grap_dev/odoo-eshop-8.0/env/lib/python2.7/site-packages/werkzeug/serving.py", line 226, in write
    self.send_header(key, value)
  File "/usr/lib/python2.7/BaseHTTPServer.py", line 412, in send_header
    self.wfile.write("%s: %s\r\n" % (keyword, value))
IOError: [Errno 32] Broken pipe
```
Todo : Investigate. Maybe a problem with werkzeug.

https://stackoverflow.com/questions/37962925/flask-app-get-ioerror-errno-32-broken-pipe

* Finish account part

* Check if we delete unpack feature

* Recheck all

* Deploy on erp-test and check with PZI

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
