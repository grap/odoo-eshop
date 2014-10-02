#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from ConfigParser import ConfigParser
from os.path import isfile, expanduser


def read_config(filename=None):
    config_file = filename
    if config_file is None:
        config_file = expanduser('~/.odoo_eshop.ini')
        if not isfile(config_file):
            config_file = '/etc/odoo_eshop/config.ini'
    assert isfile(config_file), (
        'Could not find config file (looking at %s)' % (
            config_file or '~/.odoo_eshop.ini and /etc/odoo_eshop/config.ini'
        )
    )

    conf = ConfigParser()
    conf.read(config_file)
    return conf


conf = read_config()
