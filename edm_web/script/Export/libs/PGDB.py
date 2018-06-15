#-*- coding: utf8 -*-

import os
import redis
import MySQLdb
import psycopg2
import DBUtils.PooledDB


remote_pg = {
    "host": "192.168.50.64",
    "port": 5432,
    "user": "mm-log",
    "password": "3ViVTOdrA0L2",
    "dbname": "mm-log",
}

locale_pg = {
    "host": "192.168.50.51",
    "port": 5432,
    "user": "mm-log",
    "password": "3ViVTOdrA0L2",
    "dbname": "mm-log",
}


remPgPool = DBUtils.PooledDB.PooledDB(psycopg2, 1, **remote_pg)
locPgPool = DBUtils.PooledDB.PooledDB(psycopg2, 1, **locale_pg)


def _get_conn(db_type):
    if db_type == 'rem_pg':
        return remPgPool.connection()
    elif db_type == 'loc_pg':
        return locPgPool.connection()
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

