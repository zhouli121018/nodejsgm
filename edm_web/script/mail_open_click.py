# -*- coding: utf-8 -*-

"""
邮箱活跃度统计
每周执行一次
/usr/local/pyenv/versions/edm_web/bin/python /usr/local/edm_web/script/email_open_click.py
"""

from gevent import monkey
monkey.patch_all()

import gevent
import gevent.pool

import os
import sys
import time
import math
import logging
import datetime
import traceback

import django
ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../edm_web'))
sys.path.append(ROOT)
SCRIPT = os.path.join(ROOT, 'script')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edm_web.settings")
django.setup()

from django.db import InterfaceError, DatabaseError, connections

from app.other.models import EmailOpenClickTemp, EmailOpenClick, EmailActivitySettings
# from django.db.models import F, Count, Sum
from django.conf import settings
from tagging.models import Tag, TagCategory
from app.other.models import AdressPool, AttributePool, AdressAttributeRelation
from django_redis import get_redis_connection
redis = get_redis_connection()

from lib import pidfile, tools

# 全局变量
log = None
signal_stop = False
_TABLES = None
_START_TIME = None

_MAXTHREAD = 10
_PG_DB_NAME = 'pgsql-ms'
_TRACK_DB_NAME = 'mm-track'

_email_open_setting = None
_email_click_setting = None

# ###########################################################
# 处理器
class Processor(object):

    def __init__(self, table):
        self.uid, self.track, self.type = table.split('_')
        # self.start_time = time.time()
        if self.type == 'email':
            sql = "SELECT email, COUNT(email) FROM {0} WHERE open_first>'{1}' GROUP BY email;".format(table, _START_TIME)
        elif self.type == 'click':
            sql = """
            SELECT track_email.email, SUM(track_click.click_unique) AS click_unique
            FROM {0}_track_click track_click
            INNER JOIN {0}_track_email track_email ON track_email.email_id = track_click.email_id
            WHERE track_click.click_first>'{1}'
            GROUP BY track_email.email;
            """.format(self.uid, _START_TIME)
        self.lists = db_query(_TRACK_DB_NAME, sql)

    def handle(self):
        if self.type == 'email':
            count = 0
            values = []
            for l in self.lists:
                values.append(EmailOpenClickTemp(email=l[0], opens=l[1], clicks=0))
                if count == 5000:
                    EmailOpenClickTemp.objects.bulk_create(values)
                    count = 0
                    values = []
                    continue
                count += 1
            if values:
                EmailOpenClickTemp.objects.bulk_create(values)
        if self.type == 'click':
            count = 0
            values = []
            for l in self.lists:
                values.append(EmailOpenClickTemp(email=l[0], opens=0, clicks=l[1]))
                if count == 5000:
                    EmailOpenClickTemp.objects.bulk_create(values)
                    count = 0
                    values = []
                    continue
                count += 1
            if values:
                EmailOpenClickTemp.objects.bulk_create(values)
        # log.info('end handle: table={}_{}_{}, time={}'.format(self.uid, self.track, self.type, time.time()-self.start_time))
        return

def worker(table):
    try:
        log.info('start handle: table={}'.format(table))
        p = Processor(table)
        p.handle()
    except (DatabaseError, InterfaceError), e:
        reconnect()
        log.error(u'Database error...')
        log.error(traceback.format_exc())
        gevent.sleep(10)
        return
    except:
        log.error(u'handle error: table={}'.format(table))
        log.error(traceback.format_exc())
    return

def scanner():
    pool = gevent.pool.Pool(_MAXTHREAD)
    for t in _TABLES:
        if signal_stop: break
        pool.spawn(worker, t)
        gevent.sleep(0.01)
    pool.join()
    return

############################################################
# 初始化活跃度设置
def init_settings():
    global _email_open_setting, _email_click_setting
    _email_open_setting, _email_click_setting = [], []
    lists = EmailActivitySettings.objects.all().order_by('level')
    for d in lists:
        _email_open_setting.append({
            'level': d.level,
            'low': d.open_low,
            'high': d.open_high,
        })
        _email_click_setting.append({
            'level': d.level,
            'low': d.click_low,
            'high': d.click_high,
        })
    log.info('init open settings: {}'.format(_email_open_setting))
    log.info('init click settings: {}'.format(_email_click_setting))

def init_settings_router():
    while True:
        try:
            log.info('init resouce routine')
            init_settings()
        except BaseException as e:
            log.error('init_resource_routine exception')
        gevent.sleep(600)

# ###########################################################
# 初始化
def init():
    global _START_TIME, _TABLES

    _START_TIME = '{} 00:00:00'.format((datetime.datetime.today() + datetime.timedelta(days=-200)).strftime('%Y-%m-%d'))

    sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='{}' AND table_name LIKE '%_track_email';".format(_TRACK_DB_NAME)
    lists = db_query(_TRACK_DB_NAME, sql)
    emails = [t[0] for t in lists]

    sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='{}' AND table_name LIKE '%_track_click';".format(_TRACK_DB_NAME)
    lists = db_query(_TRACK_DB_NAME, sql)
    clicks = [t[0] for t in lists]
    emails.extend(clicks)
    _TABLES = emails

    for table, type in [('email_open_click', '1'), ('email_open_click_temp', '2')]:
        init_table(table, type)

# 初始化表
def init_table(table, type):
    """
    删除约束： ALTER TABLE tablename DROP CONSTRAINT tablename_field_key;
    删除索引：DROP INDEX tablename_email_like;
    """
    table_sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' and table_name = '{0}';".format(table)
    res = db_query(_PG_DB_NAME, table_sql)
    if res:

        try:
            log.info('drop table: {}'.format(table))
            dele_data = "DROP TABLE {0};".format(table)
            db_execute(_PG_DB_NAME, dele_data)

            log.info("start create table: {}".format(table))
            create_sql = """
            CREATE TABLE "{0}" (
                "id" serial NOT NULL PRIMARY KEY,
                "email" varchar(100) NOT NULL,
                "opens" integer NOT NULL,
                "clicks" integer NOT NULL,
                "activity" integer NOT NULL
            );""".format(table)
            db_execute(_PG_DB_NAME, create_sql)
        except Exception as e:
            log.error(traceback.format_exc())
            sys.exit(1)
    else:
        try:
            log.info("start create table: {}".format(table))
            create_sql = """
            CREATE TABLE "{0}" (
                "id" serial NOT NULL PRIMARY KEY,
                "email" varchar(100) NOT NULL,
                "opens" integer NOT NULL,
                "clicks" integer NOT NULL,
                "activity" integer NOT NULL
            );""".format(table)
            db_execute(_PG_DB_NAME, create_sql)
        except Exception as e:
            log.error(traceback.format_exc())
            sys.exit(1)

    # 查询索引
    index_sql = """
    SELECT t.relname AS table_name,
            c.relname AS index_name
    FROM (
          SELECT relname,indexrelid
          FROM pg_index i, pg_class c
          WHERE c.relname = '{0}' AND indrelid = c.oid
    ) t, pg_index i,pg_class c
    WHERE t.indexrelid = i.indexrelid AND i.indexrelid = c.oid AND c.relname='{0}_{1}_like';
    """.format(table, 'email')
    res = db_query(_PG_DB_NAME, index_sql)
    if res:
        try:
            log.info('drop index on table: {}'.format(table))
            drop_index = "DROP INDEX {0}_{1}_like;".format(table, 'email');
            db_execute(_PG_DB_NAME, drop_index)
        except Exception as e:
            log.error(traceback.format_exc())
            sys.exit(1)

    # 查询唯一约束
    if type =='1':
        constrait_sql = "SELECT * FROM pg_constraint WHERE conname = '{0}_{1}_key';".format(table, 'email')
        res = db_query(_PG_DB_NAME, constrait_sql)
        if res:
            try:
                log.info('drop unique index on table: {}'.format(table))
                drop_unique = "ALTER TABLE {0} DROP CONSTRAINT {0}_{1}_key;".format(table, 'email')
                db_execute(_PG_DB_NAME, drop_unique)
            except Exception as e:
                log.error(traceback.format_exc())
                sys.exit(1)

############################################################
# 完成表创建
def init_finish(table, type):
    """
    唯一约束： CREATE UNIQUE INDEX tablename_field_key ON tablename USING btree (field);
    索引： CREATE INDEX tablename_email_like ON tablename USING btree (field varchar_pattern_ops)；
    """

    # 查询索引
    index_sql = """
        SELECT t.relname AS table_name,
                c.relname AS index_name
        FROM (
              SELECT relname,indexrelid
              FROM pg_index i, pg_class c
              WHERE c.relname = '{0}' AND indrelid = c.oid
        ) t, pg_index i,pg_class c
        WHERE t.indexrelid = i.indexrelid AND i.indexrelid = c.oid AND c.relname='{0}_{1}_like';
        """.format(table, 'email')
    res = db_query(_PG_DB_NAME, index_sql)
    if not res:
        try:
            log.info('create index on table: {}'.format(table))
            create_index = "CREATE INDEX {0}_{1}_like ON {0} USING btree ({1} varchar_pattern_ops);".format(table, 'email');
            db_execute(_PG_DB_NAME, create_index)
        except Exception as e:
            log.error(traceback.format_exc())
            sys.exit(1)

    # 查询唯一约束
    if type =='1':
        constrait_sql = "SELECT * FROM pg_constraint WHERE conname = '{0}_{1}_key';".format(table, 'email')
        res = db_query(_PG_DB_NAME, constrait_sql)
        if not res:
            try:
                log.info('create unique index on table: {}'.format(table))
                create_unique = "CREATE UNIQUE INDEX {0}_{1}_key ON {0} USING btree ({1});".format(table, 'email')
                db_execute(_PG_DB_NAME, create_unique)
            except Exception as e:
                log.error(traceback.format_exc())
                sys.exit(1)

# 打开、点击统计
def init_insert(tablename, tablename_tmp):
    log.info('start insert data to table={}'.format(tablename))
    sql = """
    INSERT INTO {0}(email, opens, clicks, activity)
    SELECT email, SUM(opens) AS opens, SUM(clicks) AS clicks, 0 AS activity
    FROM {1} GROUP BY email
    ;
    """.format(tablename, tablename_tmp)
    db_execute(_PG_DB_NAME, sql)

# 活跃度计算
def init_activity(tablename):
    log.info('start run activity...')
    case_open, case_click = "", ""
    for _e in _email_open_setting:
        if int(_e['high']):
            case_open += " WHEN opens >={0} AND opens <{1} THEN {2} ".format(_e['low'], _e['high'], _e['level'])
        else:
            case_open += " WHEN opens >={0} THEN {2} ".format(_e['low'], _e['high'], _e['level'])
    for _e in _email_click_setting:
        if int(_e['high']):
            case_click += " WHEN clicks >={0} AND clicks <{1} THEN {2} ".format(_e['low'], _e['high'], _e['level'])
        else:
            case_click += " WHEN clicks >={0} THEN {2} ".format(_e['low'], _e['high'], _e['level'])
    sql = """
    WITH B AS(""" + """
       SELECT id,
                CASE WHEN opens=0 THEN 0 {1} ELSE 5 END AS activity_open,
                CASE WHEN clicks=0 THEN 0 {2} ELSE 5 END AS activity_click
       FROM {0}
    ),
    C AS(
        SELECT id, CASE WHEN activity_open > activity_click THEN activity_open ELSE activity_click END AS activity FROM B
     )
    UPDATE {0}
    SET activity = C.activity
    FROM C WHERE {0}.id = C.id;
    """.format(tablename, case_open, case_click)
    log.info('init activity sql:\n{}'.format(sql))
    db_execute(_PG_DB_NAME, sql)
    log.info('end run activity...')
    log.info('print start time: {}'.format(_START_TIME))

# 活跃度 地址入库
def mail_store_worker(res, tag_item_vals):
    bulk_count = 0
    bulk_lists = []
    for row in res:
        address, activity = row
        email_obj, _created = AdressPool.objects.get_or_create(email=address)
        activity = int(activity)
        if activity in tag_item_vals:
            tag_vals = tag_item_vals[activity]
            _obj, _created = AttributePool.objects.get_or_create(category='activity', category_id=tag_vals['category_id'], tag_id=tag_vals['tag_id'])
            bulk_lists.append(AdressAttributeRelation(email=email_obj, attribute=_obj))
            bulk_count += 1
        if bulk_count >= 3000:
            AdressAttributeRelation.objects.bulk_create(bulk_lists)
            bulk_count = 0
            bulk_lists = []
    if bulk_lists:
        AdressAttributeRelation.objects.bulk_create(bulk_lists)
    return

def finish_mail_store():
    # 删除历史记录
    log.info('Mail_Store delete customer_id=0, list_id=0')
    AdressAttributeRelation.objects.filter(list_id=0).delete()

    tag_item_vals = {}
    tag_lists = Tag.objects.filter(category__category='activity')
    for d in tag_lists:
        if d.name == u'一星':
            activity = 1
        elif d.name == u'二星':
            activity = 2
        elif d.name == u'三星':
            activity = 3
        elif d.name == u'四星':
            activity = 4
        elif d.name == u'五星':
            activity = 5
        else:
            activity = 3
        tag_item_vals.update({
            activity : {
                'category': d.category.category,
                'category_id': d.category_id,
                'tag_id': d.id,
                'category_name': d.category.name,
                'tag_name': d.name,
                'isremark': d.isremark,
            }
        })

    log.info('Mail_Store start customer_id=0, list_id=0')
    sql_count = """ SELECT count(1) FROM email_open_click;"""
    res_count = db_query(_PG_DB_NAME, sql_count)
    res_count = res_count[0][0]
    _max_head = 50
    pool = gevent.pool.Pool(50)
    avg_line = int(math.ceil(float(res_count)/float(_max_head)))
    for index in xrange(_max_head+1):
        if signal_stop: break
        start_index = avg_line*index
        sql = """ SELECT email, activity FROM email_open_click ORDER BY id DESC LIMIT {} OFFSET {};""".format(avg_line, start_index)
        res = db_query(_PG_DB_NAME, sql)
        if res:
            pool.spawn(mail_store_worker, res, tag_item_vals)
    pool.join()
    return

def finish():
    tablename = 'email_open_click'
    tablename_tmp = 'email_open_click_temp'

    init_finish(tablename_tmp, '2')

    gevent.sleep(0.1)

    init_insert(tablename, tablename_tmp)

    gevent.sleep(0.1)

    init_activity(tablename)

    gevent.sleep(0.1)

    init_finish(tablename, '1')

    gevent.sleep(0.1)

    t1 = time.time()
    finish_mail_store()
    log.info('Mail_Store end customer_id=0, list_id=0, time={}'.format(time.time()-t1))

############################################################
# 数据库重启
def reconnect():
    try:
        log.info(u'Restoring the Mysql Connection start')
        cursor = connections['mm-ms'].cursor()
        db = cursor.db
        if db.connection is None or not db.is_usable():
            db.close_if_unusable_or_obsolete()
            with db.wrap_database_errors:
                db.connect()
            log.info(u'Restoring the Mysql Connection end')
            gevent.sleep(10)
    except Exception as e:
        log.warning(u'DB Connection error', exc_info=1)

def reconnect_pool():
    try:
        log.info(u'Restoring the Mysql mm-pool Connection start')
        cursor = connections['mm-pool'].cursor()
        db = cursor.db
        if db.connection is None or not db.is_usable():
            db.close_if_unusable_or_obsolete()
            with db.wrap_database_errors:
                db.connect()
            log.info(u'Restoring the Mysql mm-pool Connection end')
            gevent.sleep(10)
    except Exception as e:
        log.warning(u'DB Connection error', exc_info=1)

def reconnect_pgsql():
    try:
        log.info(u'Restoring the postgreSQL Connection start')
        cursor = connections['pgsql-ms'].cursor()
        db = cursor.db
        if db.connection is None or not db.is_usable():
            db.close_if_unusable_or_obsolete()
            with db.wrap_database_errors:
                db.connect()
            log.info(u'Restoring the postgreSQL Connection end')
            gevent.sleep(10)
    except Exception as e:
        log.warning(u'DB Connection error', exc_info=1)

############################################################
# 获取数据库游标
def get_ms_cr(db_type):
    cr = connections[db_type].cursor()
    db = cr.db
    if db.connection is None or not db.is_usable():
        db.close_if_unusable_or_obsolete()
        with db.wrap_database_errors:
            db.connect()
        cr = connections[db_type].cursor()
        log.info(u'reconnect {} Connection end'.format(db_type))
    return cr

############################################################
# 安全调用对象
def safe_call(fn, *args, **kwargs):
    try :
        return fn(*args, **kwargs)
    except Exception, e:
        log.error('call "%s" failure\n %s' % (fn.__name__, e.message))
        log.error(traceback.format_exc())
        return None

# 等待调用成功 (有超时时间)
def time_call(fn, *args, **kwargs):
    try_count = 3
    while try_count > 0 :
        res = safe_call(fn, *args, **kwargs)
        if res is not None:
            return res
        log.error('try call "%s" count: %d' % (fn.__name__, try_count))
        try_count -= 1
        gevent.sleep(3)
    return

# 等待调用成功 (无超时时间)
def wait_call(fn, *args, **kwargs):
    while True :
        res = safe_call(fn, *args, **kwargs)
        if res is not None:
            return res
        gevent.sleep(3)
    return

# ###########################################################
# 数据库查询
def db_query(db_name, sql, param=None):
    cr = time_call(get_ms_cr, db_name)
    cr.execute(sql, param)
    return cr.fetchall()

def db_execute(db_name, sql, param=None):
    cr = time_call(get_ms_cr, db_name)
    cr.execute(sql, param)
    return

############################################################
# 日志设置
def set_logger(log_file, is_screen=True):
    global log
    log = logging.getLogger('mail_open_click')
    log.setLevel(logging.INFO)
    format = logging.Formatter('%(asctime)-15s %(levelname)s %(message)s')

    log_handler = logging.handlers.RotatingFileHandler(log_file, 'a', 20000000, 4)
    log_handler.setFormatter(format)
    log.addHandler(log_handler)
    sys.stdout = open(log_file, 'a')

    if is_screen:
        log_handler = logging.StreamHandler()
        log_handler.setFormatter(format)
        log.addHandler(log_handler)

############################################################
# 信号量处理
def signal_handle(mode):
    log.info(u"Catch signal: %s" % mode)
    global signal_stop
    signal_stop = True

############################################################
def main():
    log_dir = os.path.join(SCRIPT, 'log')
    pid_dir = os.path.join(SCRIPT, 'pid')
    log_file = os.path.join(log_dir, 'mail_open_click.log')
    pid_file = os.path.join(pid_dir, 'mail_open_click.pid')

    tools.make_dir([log_dir, pid_dir])
    set_logger(log_file)
    pidfile.register_pidfile(pid_file)

    init()
    init_settings()
    gevent.spawn(init_settings_router)

    log.info(u'program start...')
    EXIT_CODE = 0
    try:
        scanner()
        finish()
    except KeyboardInterrupt:
        signal_handle('sigint')
    except:
        log.error(traceback.format_exc())
        EXIT_CODE = 1
    log.info(u"program quit...")
    sys.exit(EXIT_CODE)

if __name__ == "__main__":
    main()
