# -*- coding: utf-8 -*-
#
import logging
import logging.handlers
from logging.handlers import RotatingFileHandler

# 日志
def getLogger(name, logfile=None):
    _handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)s %(message)s')
    _handler.setFormatter(formatter)

    log = logging.getLogger(name)
    log.addHandler(_handler)
    if logfile:
        Rthandler = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=5)
        Rthandler.setFormatter(formatter)
        log.addHandler(Rthandler)
    log.setLevel(logging.DEBUG)
    return log
