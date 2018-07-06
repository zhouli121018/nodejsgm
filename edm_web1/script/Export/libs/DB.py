#-*- coding: utf8 -*-

import os
import redis
import MySQLdb
import psycopg2
import DBUtils.PooledDB

remote_sql = {
    "host": "192.168.50.64",
    "port": 3306,
    "user": "edm_web",
    "passwd": "XnLaT34LxaQViNB",
    "db": "mm-pool",
}

remote_sqlms = {
    "host": "192.168.50.64",
    "port": 3306,
    "user": "edm_web",
    "passwd": "XnLaT34LxaQViNB",
    "db": "mm-ms",
}

local_sql = {
    "host": "192.168.50.51",
    "port": 3306,
    "user": "edm_web",
    "passwd": "XnLaT34LxaQViNB",
    "db": "mm-ms",
}

local_pgsql = {
    "host": "192.168.50.51",
    "port": 5432,
    "user": "mm-ms",
    "password": "3ViVTOdrA0L2",
    "dbname": "mm-ms",
}

remote_mypool = DBUtils.PooledDB.PooledDB(MySQLdb, 1, charset='utf8', **remote_sql)
remote_myms = DBUtils.PooledDB.PooledDB(MySQLdb, 1, charset='utf8', **remote_sqlms)
local_mypool = DBUtils.PooledDB.PooledDB(MySQLdb, 1, charset='utf8', **local_sql)
local_pgpool = DBUtils.PooledDB.PooledDB(psycopg2, 1, **local_pgsql)

def _get_conn(db_type):
    if db_type == 'remote_mysql':
        return remote_mypool.connection()
    elif db_type == 'remote_myms':
        return remote_myms.connection()
    elif db_type == 'local_mysql':
        return local_mypool.connection()
    elif db_type == 'local_pgsql':
        return local_pgpool.connection()
    return None

def query(db_type, sql, args=()):
    conn = _get_conn(db_type)
    cursor = conn.cursor()
    cursor.execute(sql, args)
    rs = cursor.fetchall()
    cursor.close()
    conn.close()
    return rs

def queryone(db_type, sql, args=()):
    res = query(db_type, sql, args)
    return res and res[0] or None

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

redis_db = redis.Redis( host="127.0.0.1",  port=6379)
