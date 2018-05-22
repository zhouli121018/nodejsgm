# coding=utf-8
"""
根据mail model 同步数据库
"""
import datetime
import lib.common         as Common

Common.init_django_enev()
from django.db import connection

def add_is_study():
    """
    2015-11-19
    增加字段is_study 是否提交dspam学习
    :return:
    """
    sql = 'ALTER TABLE "public"."{}" ADD COLUMN "is_study" boolean'
    today = datetime.date.today()
    cursor = connection.cursor()
    for i in range(0, 30):
        date = (today - datetime.timedelta(days=i)).strftime('%Y%m%d')
        print date
        try:
            cursor.execute(sql.format('mail_{}'.format(date)))
        except BaseException, e:
            print e
        try:
            cursor.execute(sql.format('cmail_{}'.format(date)))
        except BaseException, e:
            print e
    connection.commit()
    cursor.close()
    connection.close()


def add_dspam_study():
    """
    2015-11-19
    增加字段dspam_study dspam学习结果(上面的字段is_study作废)
    :return:
    """
    sql = 'ALTER TABLE "public"."{}" ADD COLUMN "dspam_study" SmallInt default 0'
    today = datetime.date.today()
    cursor = connection.cursor()
    for i in range(0, 30):
        date = (today - datetime.timedelta(days=i)).strftime('%Y%m%d')
        print date
        try:
            cursor.execute(sql.format('mail_{}'.format(date)))
        except BaseException, e:
            print e
        try:
            cursor.execute(sql.format('cmail_{}'.format(date)))
        except BaseException, e:
            print e
    connection.commit()
    cursor.close()
    connection.close()


def add_sender_name():
    """
    2015-11-20
    增加字段sender_name 邮件内容里的发件人姓名
    :return:
    """
    sql = 'ALTER TABLE "public"."{}" ADD COLUMN "sender_name" Varchar(50)'
    today = datetime.date.today()
    cursor = connection.cursor()
    for i in range(0, 30):
        date = (today - datetime.timedelta(days=i)).strftime('%Y%m%d')
        print date
        try:
            cursor.execute(sql.format('mail_{}'.format(date)))
        except BaseException, e:
            print e
        try:
            cursor.execute(sql.format('cmail_{}'.format(date)))
        except BaseException, e:
            print e
    connection.commit()
    cursor.close()
    connection.close()


def add_customer_report():
    """
    2015-12-221
    增加字段customer_report 客户举报字段
    :return:
    """
    sql = 'ALTER TABLE "public"."{}" ADD COLUMN "customer_report" SmallInt default 0'
    today = datetime.date.today()
    cursor = connection.cursor()
    for i in range(0, 30):
        date = (today - datetime.timedelta(days=i)).strftime('%Y%m%d')
        print date
        try:
            cursor.execute(sql.format('mail_{}'.format(date)))
        except BaseException, e:
            print e
        try:
            cursor.execute(sql.format('cmail_{}'.format(date)))
        except BaseException, e:
            print e
    connection.commit()
    cursor.close()
    connection.close()

def add_server_id():
    """
    2015-12-221
    增加字段 server_id 邮件所在服务器ID
    :return:
    """
    sql = 'ALTER TABLE "public"."{}" ADD COLUMN "server_id" Varchar(20)'
    today = datetime.date.today()
    cursor = connection.cursor()
    for i in range(0, 30):
        date = (today - datetime.timedelta(days=i)).strftime('%Y%m%d')
        print date
        try:
            cursor.execute(sql.format('mail_{}'.format(date)))
        except BaseException, e:
            print e
        try:
            cursor.execute(sql.format('cmail_{}'.format(date)))
        except BaseException, e:
            print e
    connection.commit()
    cursor.close()
    connection.close()


def add_review():
    """
    2016-01-27
    增加字段 reviewer, review_time 邮件所在服务器ID
    :return:
    """
    sql = """
    ALTER TABLE "public"."{}"
    ADD COLUMN "reviewer_id" Int,
    ADD FOREIGN KEY (reviewer_id) REFERENCES public.auth_user(id),
    ADD COLUMN "review_time" timestamp with time zone
    """
    today = datetime.date.today()
    cursor = connection.cursor()
    for i in range(0, 30):
        date = (today - datetime.timedelta(days=i)).strftime('%Y%m%d')
        print date
        try:
            cursor.execute(sql.format('mail_{}'.format(date)))
        except BaseException, e:
            print e
        try:
            cursor.execute(sql.format('cmail_{}'.format(date)))
        except BaseException, e:
            print e
    connection.commit()
    cursor.close()
    connection.close()

def add_bulk_sample():
    """
    2016-02-24
    增加字段bulk_sample 是否为群发样本
    :return:
    """
    sql = 'ALTER TABLE "public"."{}" ADD COLUMN "bulk_sample" boolean default false'
    today = datetime.date.today()
    cursor = connection.cursor()
    for i in range(0, 30):
        date = (today - datetime.timedelta(days=i)).strftime('%Y%m%d')
        print date
        try:
            cursor.execute(sql.format('mail_{}'.format(date)))
        except BaseException, e:
            print e
        # try:
        #     cursor.execute(sql.format('cmail_{}'.format(date)))
        # except BaseException, e:
        #     print e
    connection.commit()
    cursor.close()
    connection.close()

def add_attach_name():
    """
    2016-04-29
    增加字段attach_name 所有附件名称
    :return:
    """
    sql = 'ALTER TABLE "public"."{}" ADD COLUMN "attach_name" Text'
    today = datetime.date.today()
    cursor = connection.cursor()
    for i in range(0, 30):
        date = (today - datetime.timedelta(days=i)).strftime('%Y%m%d')
        print date
        try:
            cursor.execute(sql.format('mail_{}'.format(date)))
        except BaseException, e:
            print e
        try:
            cursor.execute(sql.format('cmail_{}'.format(date)))
        except BaseException, e:
            print e
    connection.commit()
    cursor.close()
    connection.close()


def add_is_del_attach():
    """
    2016-08-16
    增加字段is_del_attach 是否删除附件
    :return:
    """
    sql = 'ALTER TABLE "public"."{}" ADD COLUMN "is_del_attach" boolean default false'
    today = datetime.date.today()
    cursor = connection.cursor()
    for i in range(0, 30):
        date = (today - datetime.timedelta(days=i)).strftime('%Y%m%d')
        print date
        try:
            cursor.execute(sql.format('mail_{}'.format(date)))
        except BaseException, e:
            print e
    connection.commit()
    cursor.close()
    connection.close()

def add_bounce():
    """
    2017-06-14 网关mail增加bounce 字段
    :return:
    """
    sql = """
    ALTER TABLE "public"."{}"
    ADD COLUMN "bounce_result" Varchar(20),
    ADD COLUMN "bounce_time" timestamp with time zone,
    ADD COLUMN "bounce_message" Text
    """
    today = datetime.date.today()
    cursor = connection.cursor()
    for i in range(0, 30):
        date = (today - datetime.timedelta(days=i)).strftime('%Y%m%d')
        print date
        try:
            cursor.execute(sql.format('cmail_{}'.format(date)))
        except BaseException, e:
            print e
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    add_bounce()
