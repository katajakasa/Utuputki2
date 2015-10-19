# -*- coding: utf-8 -*-

import sys
import os
import pytz
import isodate
import datetime
import binascii


def utc_now():
    """ Gets UTC datetime """
    return pytz.utc.localize(datetime.datetime.utcnow())


def utc_minus_delta(seconds):
    """ Gets UTC datetime with deltatime substracted """
    return pytz.utc.localize(datetime.datetime.utcnow() - datetime.timedelta(seconds=seconds))


def to_isodate(dt):
    """ Converts datetime to iso8601-timestamp """
    return isodate.datetime_isoformat(dt)


def from_isodate(ts):
    """ Parses timestamp to datetime """
    return isodate.parse_datetime(ts)


def decode_path(name):
    """ Attempt to decode path with correct encoding """
    return name.decode(sys.getfilesystemencoding())


def get_or_create(session, model, **kwargs):
    """ Gets an instance if it exists, or creates a new one if not. """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def generate_session():
    """ Generates a session ID. Secure enough. """
    return binascii.hexlify(os.urandom(16))

