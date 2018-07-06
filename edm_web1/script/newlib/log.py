# -*- coding: utf-8 -*-
#
import logging
import logging.handlers

# 日志
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)s %(message)s'))

log = logging.getLogger('LOG')
log.addHandler(_handler)
log.setLevel(logging.DEBUG)
