sudo apt-get install redis-server -y
# support uwsgi + pcre (https://stackoverflow.com/questions/21669354/rebuild-uwsgi-with-pcre-support)
sudo apt-get install sudo apt-get install libpcre3 libpcre3-dev -y

virtualenv env --python=python3.7
./env/bin/pip install -r ./requirements.txt
mkdir ./odoo_eshop/eshop_app/static/odoo_data/
cp ./config/config.ini.sample ./config/config.ini
