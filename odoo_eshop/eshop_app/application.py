from datetime import timedelta

from flask import Flask
from flask_babel import Babel
from flask_caching import Cache

from .tools.config import conf

app = Flask(__name__)
app.secret_key = conf.get("flask", "secret_key")
app.debug = conf.get("flask", "debug") == "True"
app.config["BABEL_DEFAULT_LOCALE"] = conf.get("localization", "locale")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    minutes=int(conf.get("auth", "session_minute"))
)

babel = Babel(app)

cache = Cache(
    app,
    config={
        "CACHE_TYPE": conf.get("cache", "cache_type"),
        "CACHE_DEFAULT_TIMEOUT": int(conf.get("cache", "cache_default_timeout")),
        "CACHE_KEY_PREFIX": conf.get("cache", "cache_key_prefix"),
    },
)

# Clear Cache and reprefetch data (For test purpose)
# cache.clear()

from .models.models import prefetch_all  # noqa: E402

prefetch_all()
