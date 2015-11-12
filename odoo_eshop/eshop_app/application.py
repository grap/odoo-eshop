#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Lib
from datetime import timedelta

# Extra Lib
from flask import Flask
from flask.ext.babel import Babel
from flask.ext.cache import Cache

# Custom Tools
from tools.config import conf

# Create Aplication
app = Flask(__name__)
app.secret_key = conf.get('flask', 'secret_key')
app.debug = conf.get('flask', 'debug') == 'True'
app.config['BABEL_DEFAULT_LOCALE'] = conf.get('localization', 'locale')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
    minutes=int(conf.get('auth', 'session_minute')))

# Manage translation for the new application
babel = Babel(app)

# Manage Cache for the new application
cache = Cache(app, config={'CACHE_TYPE': conf.get('cache', 'method')})

# Clear Cache
cache.clear()
