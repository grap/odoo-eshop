.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==============
{module_title}
==============

This app is a Flask Website that communicate with Odoo, to provide
a light eShop.

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
- Cache with Redis, to reduce Odoo call.


Installation
============

eshop Installation
------------------

```
pip install -r requirements.txt

apt-get install redis-server
```

Odoo Installation
-----------------

This version is compatible with an Odoo 7.0 with the following modules
installed :

mandatory modules

- sale_eshop (mandatory)

Optional modules

- sale_food
- sale_recovery_moment

Note, you should change somes controlers and templates, if you don't want
to install this modules.

Roadmap / Know Issues
=====================

* controller_technical.py
    * l'url d'image renvoie un fichier à télécharger, plutot qu'une image
      a afficher;
    * IMPORTANT le code est toujours 200, et devrait être 304 pour alléger la
      charge serveur + réduire le transfert;

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
