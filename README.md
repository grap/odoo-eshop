# Odoo Eshop

.. |badge1| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1|

This app is a Flask Website that communicate with Odoo, to provide
a light eShop.


## Main Features

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

## Technical caracteristics

- This version is compatible with an Odoo 16.0 with the following module
installed ``sale_eshop`` available here : https://github.com/grap/grap-odoo-business
- Do not host database, datas are requested on the fly to the odoo instance.
- Use Jinja as a template language (http://jinja.pocoo.org/docs/2.10/)

## Installation for development

### Dependencies

```
sudo apt install python3.12 python3.12-dev python3.12-venv letsencrypt nginx
mkdir /var/www/letsencrypt
```

### Eshop Folder

```
git clone https://github.com/grap/odoo-eshop -b 16.0
cd odoo-eshop && ./install.sh
```

### Eshop Configuration

in the config.ini file of the eshop, set the :

* ``[odoo] url`` : the url (and the port) of your odoo instance
* ``[odoo] database`` : the database name you want to connect
* ``[odoo] company_id`` : the odoo company ID want to connect

* ``[auth] user_login`` : the login of the eshop User
* ``[auth] user_password`` : the password of the eshop User


### Launch eshop

``./env/bin/python -m odoo_eshop``

## Installation on server

## TODO 
How to install on server : eshop user, pip install, Systemctl file, daemon

Same as for development at start.
One Eshop Folder per company having an eshop. 

## Odoo config

In odoo.cfg, add two parameters (per eshop) under `[ir.config_parameter]`

Here is the pattern

```
sale_eshop.eshop_url__{{odoo_instance.odoo_database_prefix}}__{{eshop.odoo_company_id}} = https://{{eshop.server_name}}/
sale_eshop.eshop_invalidation_key__{{odoo_instance.odoo_database_prefix}}__{{eshop.odoo_company_id}} = {{eshop_secrets[ansible_hostname][odoo_instance.name][eshop.name]['invalidation_key']}}
```

For example :

```
sale_eshop.eshop_url__caap__8 = https://boutique-new.lecoindulevain.fr/
sale_eshop.eshop_invalidation_key__caap__8 = CLStRAv3Kh6hpz7_PREPROD_CDL
```

## Nginx config

Two example files to handle http and https

First for http


```
# Redirect Call from an Unsecure URL to a secure One
# Use this setting in production
server {
    listen 80;
    server_name {{eshop.server_name}};

    location ^~ /.well-known/acme-challenge {
        default_type text/plain;
        root {{letsencrypt_folder}};
    }

    location / {
        return 302 https://$server_name$request_uri;
    }

    # Strict Transport Security
    # Previous Setting...
    # add_header Strict-Transport-Security max-age=2592000;
    # rewrite ^/.*$ https://$host$request_uri? permanent;
}

```

Second for https

```
server {
    listen                      443;
    server_name                 {{eshop.server_name}};

    # Time Out
    keepalive_timeout           600;

    # Log File
    access_log                  /var/log/nginx/{{eshop.server_name}}.access.log;
    error_log                   /var/log/nginx/{{eshop.server_name}}.error.log;

    # SSL Files
    ssl on;

    ssl_certificate             /etc/letsencrypt/live/{{eshop.server_name}}/fullchain.pem;
    ssl_certificate_key         /etc/letsencrypt/live/{{eshop.server_name}}/privkey.pem;
    ssl_trusted_certificate     /etc/letsencrypt/live/{{eshop.server_name}}/chain.pem;

    # Proxy Buffers
    proxy_buffers               16 64k;
    proxy_buffer_size           128k;

    # Default Location
    location / {
        proxy_set_header        Host $host;
        proxy_pass              http://127.0.0.1:{{eshop.internal_port}}/;

    }
}

```

### Create service

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

### Launch

``sudo systemctl status yourEshopName.service``


### Journal

``sudo journalctl -fu yourEshopName.service``


## Credits

### Contributors

* Sylvain LE GAL
* Quentin DUPONT

Do not contact contributors directly about support or help with technical issues.


### Funders

The development of this module has been financially supported by:

* GRAP, Groupement Régional Alimentaire de Proximité (https://www.grap.coop)
* Hashbang (https://hashbang.fr)
