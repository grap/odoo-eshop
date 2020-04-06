virtualenv env --python=python2.7
./env/bin/pip install -r ./requirements.txt
mkdir ./odoo_eshop/eshop_app/static/odoo_data/
cp ./config/config.ini.sample ./config/config.ini
