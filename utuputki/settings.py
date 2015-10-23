# -*- coding: utf-8 -*-

import os
import sys
from ConfigParser import SafeConfigParser

# Find basedir
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Make SQLite database default for everything
default_db = 'sqlite:///{}'.format(os.path.join(BASEDIR, "utuputki.db"))
default_amqp = 'amqp://guest:guest@localhost:5672//'

# Config values that we should attempt to read
config_values = [
    'PORT',
    'TIMEZONE',
    'DEBUG',
    'DATABASE_CONFIG',
    'PUBLIC_PATH',
    'AMQP_URL',
    'LOG_LEVEL',
    'LOG_FILE',
    'CACHE_DIR',
    'TMP_DIR',
    'LIMIT_DURATION',
    'LIMIT_VIDEO_SIZE',
    'LIMIT_AUDIO_SIZE'
]

# Defaults
PORT = 8000
SOURCE_URL = 'http://localhost:'+str(PORT)+'/video/'
TIMEZONE = "Europe/Helsinki"
DEBUG = False
DATABASE_CONFIG = default_db
PUBLIC_PATH = os.path.join(BASEDIR, "utuputki/webui/public")
AMQP_URL = default_amqp
LOG_LEVEL = 2
LOG_FILE = 'utuputki_ui.log'
CACHE_DIR = '/tmp'
TMP_DIR = '/tmp'
LIMIT_DURATION = 1800
LIMIT_VIDEO_SIZE = 90 * 1024 * 1024
LIMIT_AUDIO_SIZE = 10 * 1024 * 1024


# Read configuration file
def config_init():
    sys.path.append(BASEDIR)
    module = sys.modules[__name__]

    parser = SafeConfigParser()
    files = parser.read(['utuputki.conf', os.path.expanduser('~/.utuputki.conf'), '/etc/utuputki.conf'])
    for m_file in files:
        print("Config: Read {} !".format(m_file))

    # Read configs and get either new value or default
    settings = {}
    for key in config_values:
        if parser.has_option('utuputki', key):
            if type(getattr(module, key)) is int:
                settings[key] = parser.getint('utuputki', key)
            elif type(getattr(module, key)) is bool:
                settings[key] = parser.getboolean('utuputki', key)
            else:
                settings[key] = parser.get('utuputki', key)
        else:
            settings[key] = getattr(module, key)

    # Put configs to globals
    for name, value in settings.iteritems():
        setattr(module, name, value)
