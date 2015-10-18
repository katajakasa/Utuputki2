# -*- coding: utf-8 -*-

import sys
import re
import os
import pytz
import isodate
import datetime
import binascii

track_matcher_1 = re.compile('([0-9]+)[\s|_]?-[\s|_]?(.*)[\s|_]?-[\s|_]?(.*)')
track_matcher_2 = re.compile('([0-9]+)[\s|_][\s|_]?(.*)')
track_matcher_3 = re.compile('(.*)[\s|_]?-[\s|_]?(.*)')


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


def match_track_filename(filename):
    """ Attempt to detect title and artist from song filename """
    m = track_matcher_1.match(filename)
    if m:
        return m.group(2), m.group(3)

    m = track_matcher_2.match(filename)
    if m:
        return None, m.group(2)

    m = track_matcher_3.match(filename)
    if m:
        return m.group(1), m.group(2)

    return None, None


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

