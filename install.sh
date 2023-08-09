virtualenv env --python=python3.7
./env/bin/pip install -r ./requirements.txt
mkdir ./odoo_eshop/eshop_app/static/odoo_data/
cp ./config/config.ini.sample ./config/config.ini

sudo apt-get install redis-server -y
