odoo-eshop
==========

POC for a Flask Website Shop that communicate with Odoo

Installation
------------

* Install Odoo;
* Install erppeek;

  pip install -U erppeek


TODO
----
    * Product quantity:
        * manage minimum_qty and rounding_qty; (and add them in sale-eshop module);

    * shopping_cart:
        * link to the product;
        * possibility to change quantity;
        * possibility to delete a row;
        * possibility to delete the whole sale order;

    * Validate the sale order:
        * select the sale_moment_recovery;

    * at login:
        * manage sale_order loading from database;
        * display sale_moment_group information;

    * Add password on res.partner and manage it;
