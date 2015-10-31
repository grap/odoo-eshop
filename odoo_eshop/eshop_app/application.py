#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Lib
from datetime import timedelta

# Extra Lib
from flask import Flask
from flask.ext.babel import Babel

# Custom Tools
from tools.config import conf


app = Flask(__name__)
app.secret_key = conf.get('flask', 'secret_key')
app.debug = conf.get('flask', 'debug') == 'True'
app.config['BABEL_DEFAULT_LOCALE'] = conf.get('localization', 'locale')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
    minutes=int(conf.get('auth', 'session_minute')))
babel = Babel(app)
