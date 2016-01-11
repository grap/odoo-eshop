#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from eshop_app.tools.config import conf
from eshop_app.application import app

# Run Apps
app.run(
    processes=10,
    host=conf.get('flask', 'host'),
    port=conf.getint('flask', 'port'),
    debug=conf.get('flask', 'debug'))
