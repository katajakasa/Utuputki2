# -*- coding: utf-8 -*-

import sys
import codecs


class Log(object):
    LEVEL_DEBUG = 0
    LEVEL_INFO = 1
    LEVEL_WARNING = 2
    LEVEL_ERROR = 3
    LOG_CHARSET = "UTF-8"

    def __init__(self, stream, level, prepend):
        self.stream = stream
        self.level = level
        self.prepend = prepend

    def write(self, mtype, msg):
        fmt_msg = unicode(mtype + self.prepend + msg + '\n')
        self.stream.write(fmt_msg.encode(self.LOG_CHARSET, "replace"))

    def debug(self, message):
        if self.level <= self.LEVEL_DEBUG:
            self.write('[D] ', message)

    def info(self, message):
        if self.level <= self.LEVEL_INFO:
            self.write('[I] ', message)

    def warning(self, message):
        if self.level <= self.LEVEL_WARNING:
            self.write('[W] ', message)

    def error(self, message):
        if self.level <= self.LEVEL_ERROR:
            self.write('[E] ', message)


class GlobalLog(Log):
    def __init__(self, logfile, level):
        if logfile:
            try:
                stream = open(logfile, mode='wb', encoding='UTF-8')
            except IOError, e:
                print("Could not open logfile for writing!")
                raise e
        else:
            stream = codecs.getwriter('utf8')(sys.stdout)
        super(GlobalLog, self).__init__(stream, level, '')


class SessionLog(Log):
    def __init__(self, global_log, sock):
        self.ses_prepend = '['+sock.ip+'] '
        super(SessionLog, self).__init__(global_log.stream, global_log.level, self.ses_prepend)

    def set_sid(self, sid):
        if sid:
            self.prepend = self.ses_prepend + '['+sid[0:6]+'] '
        else:
            self.prepend = self.ses_prepend
