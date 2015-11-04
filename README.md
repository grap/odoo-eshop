odoo-eshop
==========

POC for a Flask Website Shop that communicate with Odoo

Installation
------------

* Install Odoo;
* Install librairies;
    * sudo pip install flask
    * sudo pip install flask-babel
    * sudo pip install erppeek


* Install redis:
    * sudo apt-get install redis-server


TODO
----

* controller_technical.py
    * l'url d'image renvoie un fichier à télécharger, plutot qu'une image
      a afficher;
    * IMPORTANT le code est toujours 200, et devrait être 304 pour alléger la
      charge serveur + réduire le transfert;
