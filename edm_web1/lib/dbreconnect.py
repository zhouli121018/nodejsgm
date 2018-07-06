# -*- coding: utf-8 -*-

import sys
import time
from django.db import connections


############################################################
# 数据库重启
def reconnectDB(name):
    try:
        print >> sys.stderr, u'Restart connect DB: %s' % name
        cursor = connections[name].cursor()
        db = cursor.db
        if db.connection is None or not db.is_usable():
            db.close_if_unusable_or_obsolete()
            with db.wrap_database_errors:
                db.connect()
            print >> sys.stderr, u'Restart connect DB: %s success' % name
            time.sleep(10)
    except Exception as e:
        print >> sys.stderr, u'DB connection error'

############################################################
# 获取数据库游标
def getConnections(name):
    cr = connections[name].cursor()
    db = cr.db
    if db.connection is None or not db.is_usable():
        db.close_if_unusable_or_obsolete()
        with db.wrap_database_errors:
            db.connect()
        cr = connections[name].cursor()
        print >> sys.stderr, u'Restart connect DB: %s success' % name
    return cr