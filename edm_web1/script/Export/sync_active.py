# -*- coding: utf-8 -*-
#
from gevent import monkey
monkey.patch_all()

from libs import PGDB as DB
import gevent
import gevent.pool
from libs.log import loger
from libs._signal import init_gevent_signal

log = loger("Test")

# 全局变量
signal_stop = False
LOCALE_PG = "loc_pg"
REMOTE_PG = "rem_pg"

def worker(data):
    email, browser, os, country, simple_country, area, ip_first, ip_last, open_total, open_first, open_last = data
    sql = "SELECT email_id FROM active_emails WHERE email=%s limit 1;"
    res = DB.queryone(LOCALE_PG, sql, args=(email, ))
    if res:
        ip_last = ip_last if ip_last else ip_first
        open_last = open_last if open_last else open_first
        sql = "UPDATE active_emails SET open_total=open_total+%s, ip_last=%s, open_last=%s WHERE email=%s"
        args=(open_total, ip_last, open_last, email)
        DB.do(LOCALE_PG, sql, args)
    else:
        sql = """INSERT INTO active_emails(email, browser, os, country, simple_country, area, ip_first, ip_last, open_total, open_first, open_last) VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        args = (email, browser, os, country, simple_country, area, ip_first, ip_last, open_total, open_first, open_last)
        DB.do(LOCALE_PG, sql, args)

def scan():
    sql = "SELECT email, browser, os, country, simple_country, area, ip_first, ip_last, open_total, open_first, open_last FROM active_emails;"
    res = DB.query(REMOTE_PG, sql)
    pool = gevent.pool.Pool(50)
    for data in res:
        pool.spawn(worker, data)
    pool.join()

############################################################
# 信号量处理
def signal_handle(mode):
    log.info("catch signal: %s" % mode)
    global signal_stop
    signal_stop = True

# ----------------------------------
def main():
    init_gevent_signal(signal_handle)
    scan()

if __name__ == "__main__":
    log.info("program start...")
    main()
    log.info("program quit...")