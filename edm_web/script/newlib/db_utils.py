#-*- coding: utf8 -*-

import os
import MySQLdb
import psycopg2
import DBUtils.PooledDB
import ConfigParser
import redis

cfg = ConfigParser.ConfigParser()
cfg.read(os.path.join(os.path.dirname(__file__), '..', 'conf', 'config.conf'))

mysql_params = dict(cfg.items('mysql_ms'))
mysql_params['port'] = int(mysql_params['port'])
if 'pass' in mysql_params:
    mysql_params['passwd'] = mysql_params.pop('pass')
if 'dbname' in mysql_params:
    mysql_params['db'] = mysql_params.pop('dbname')
mysql_pool = DBUtils.PooledDB.PooledDB(MySQLdb, 1, charset='utf8', **mysql_params)


pg_log_params = dict(cfg.items('pgsql_log'))
pg_log_params['port'] = int(pg_log_params['port'])
if 'pass' in pg_log_params:
    pg_log_params['password'] = pg_log_params.pop('pass')
if 'dbname' in pg_log_params:
    pg_log_params['dbname'] = pg_log_params.pop('dbname')
pg_log_pool = DBUtils.PooledDB.PooledDB(psycopg2, 1, **pg_log_params)


pg_ms_params = dict(cfg.items('pgsql_ms'))
pg_ms_params['port'] = int(pg_ms_params['port'])
if 'pass' in pg_ms_params:
    pg_ms_params['password'] = pg_ms_params.pop('pass')
if 'dbname' in pg_ms_params:
    pg_ms_params['dbname'] = pg_ms_params.pop('dbname')
pg_ms_pool = DBUtils.PooledDB.PooledDB(psycopg2, 1, **pg_ms_params)


redis_db = redis.Redis(
    host=cfg.get('redis', 'host'),
    port=cfg.getint('redis', 'port')
)


def _get_conn(db_type):
    if db_type == 'mysql_ms':
        return mysql_pool.connection()
    elif db_type == 'pgsql_log':
        return pg_log_pool.connection()
    elif db_type == 'pgsql_ms':
        return pg_ms_pool.connection()
    return None

def query(db_type, sql, args=()):
    conn = _get_conn(db_type)
    cursor = conn.cursor()
    cursor.execute(sql, args)
    rs = cursor.fetchall()
    cursor.close()
    conn.close()
    return rs


def do(db_type, sql, args=()):
    conn = _get_conn(db_type)
    cursor = conn.cursor()
    cursor.execute(sql, args)
    conn.commit()
    cursor.close()
    conn.close()
    return True


def doMany(db_type, sql, args=[]):
    conn = _get_conn(db_type)
    cursor = conn.cursor()
    cursor.executemany(sql, args)
    conn.commit()
    cursor.close()
    conn.close()
    return True
