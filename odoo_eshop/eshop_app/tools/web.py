#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from flask import redirect, url_for

from .config import conf


def redirect_url_for(func, **args):
    base_url = conf.get('flask', 'url')
    return redirect(base_url + url_for(func, **args))
