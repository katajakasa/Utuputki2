# -*- coding: utf-8 -*-

import os
import sys
from ConfigParser import SafeConfigParser

# Find basedir
BASEDIR = os.path.dirname(os.path.abspath(__file__))

# Make SQLite database default for everything
default_db = 'sqlite:///{}'.format(os.path.join(BASEDIR, "audiostash.db"))
default_celery_backend = 'sqla+'+default_db
default_celery_broker = 'sqla+'+default_db

# Set defaults
defaults = {
    'PORT': 8000,
    'TIMEZONE': 'Europe/Helsinki',
    'DEBUG': False,
    'DATABASE_CONFIG': default_db,
    'PUBLIC_PATH': os.path.join(BASEDIR, "public"),
    'CELERY_BROKER': default_celery_broker,
    'CELERY_BACKEND': default_celery_backend
}


# Read configuration file
def config_init():
    parser = SafeConfigParser()
    files = parser.read(['utuputki.conf', os.path.expanduser('~/.utuputki.conf'), '/etc/utuputki.conf'])
    for m_file in files:
        print("Config: Read {} !".format(m_file))

    # Read configs and get either new value or default
    settings = {}
    for key, value in defaults.iteritems():
        if parser.has_option('utuputki', key):
            settings[key] = parser.get('utuputki', key)
        else:
            settings[key] = value

    # Put configs to globals
    module = sys.modules[__name__]
    for name, value in settings.iteritems():
        setattr(module, name, value)
