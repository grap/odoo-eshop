#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from flask import (
    Flask,
    g,
    request,
    redirect,
    url_for,
    flash,
    render_template,
)

from config import conf
from auth import login, logout, requires_auth

app = Flask(__name__)

app.secret_key = conf.get('flask', 'secret_key')
app.debug = conf.get('flask', 'debug') == 'True'


@app.route("/login.html", methods=['POST'])
def login_view():
    login(request.form['login'], request.form['password'])
    return redirect(request.args['return_to'])


@app.route("/logout.html")
def logout_view():
    logout()
    return redirect(url_for('hello'))


@app.route("/")
@requires_auth
def hello():
    return render_template(
        'home.html'
    )
