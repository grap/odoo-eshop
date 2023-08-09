from .eshop_app.application import app
from .eshop_app.tools.config import conf

app.run(
    host=conf.get("flask", "host"),
    port=conf.getint("flask", "port"),
    debug=conf.get("flask", "debug"),
)
