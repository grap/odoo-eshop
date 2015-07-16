from app import app
from config import conf


app.run(host=conf.get('flask', 'host'), port=conf.getint('flask', 'port'))
