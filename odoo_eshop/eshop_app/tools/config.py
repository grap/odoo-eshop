#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Lib
from os.path import dirname, isfile, expanduser, realpath

# Extra Lib
from ConfigParser import ConfigParser


def read_config():
    config_file = expanduser('~/.odoo_eshop.ini')
    if not isfile(config_file):
        config_file = '/etc/odoo_eshop/config.ini'
    if not isfile(config_file):
        config_file = dirname(realpath(__file__))\
            + '/../../../config/config.ini'
    assert isfile(config_file), (
        'Could not find config file (looking at %s)' % (
            config_file or "~/.odoo_eshop.ini', /etc/odoo_eshop/config.ini" +
            ", ./config/config.ini"
        )
    )

    conf = ConfigParser()
    conf.read(config_file)
    return conf


conf = read_config()
