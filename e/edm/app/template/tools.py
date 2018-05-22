# -*- coding: utf-8 -*-
#
import datetime
import random
from lib.tools import safe_format
from django.db import connections


def template_randnum(n=10):
    return "".join([str(random.randint(0, 9)) for i in range(n)])

def __get_sex(kwargs, sex):
    if sex == 'M':
        kwargs.update(SEX=u"男士")
    else:
        kwargs.update(SEX=u"女士")
    return kwargs

def __get_birthday(kwargs, birthday):
    if birthday: kwargs.update(BIRTHDAY=birthday.strftime('%Y-%m-%d'))
    return kwargs

def __get_kwargs(user_id, template_id, send_id, list_id, recipents, fullname):
    kwargs = {}
    kwargs.update(
        FULLNAME=fullname, RECIPIENTS=recipents, DATE=datetime.datetime.now().strftime("%Y-%m-%d"),
        RANDOM_NUMBER=template_randnum(),
        SEX='', BIRTHDAY='', PHONE='', AREA='',
        VAR1='', VAR2='', VAR3='', VAR4='', VAR5='', VAR6='', VAR7='', VAR8='', VAR9='', VAR10='',
        JOKE='', MOTTO='', NOVEL='', ENNOVEL='',
        SUBJECT_STRING=u'无标题',
        TEMPLATE_ID=template_id, USER_ID=user_id, SEND_ID=send_id, MAILLIST_ID=list_id,
    )
    if user_id and list_id and recipents:
        cr = connections['mm-pool'].cursor()
        tablename = 'ml_subscriber_' + str(user_id)
        sql = "SELECT * FROM {} WHERE address=%s AND list_id=%s".format(tablename)
        param = (recipents, list_id)
        cr.execute(sql, param)
        line = cr.fetchone()
        names = [i[0] for i in cr.description]
        if line :
            kwargs = __get_sex(kwargs, line[names.index('sex')])
            kwargs = __get_birthday(kwargs, line[names.index('birthday')])
            kwargs.update( FULLNAME=line[names.index('fullname')], PHONE=line[names.index('phone')], AREA=line[names.index('area')] )
            try:
                i = 1
                while True:
                    res = line[names.index('var{}'.format(i))]
                    kwargs.update({ "VAR{}".format(i): res })
                    i += 1
            except ValueError:
                pass
    return kwargs

# 无法正常显示 邮件内容处理
def show_mail_replace(user_id="", template_id="", send_id="", list_id="", recipents="", fullname="", html=""):
    kwargs = __get_kwargs(user_id, template_id, send_id, list_id, recipents, fullname)
    return safe_format(html, **kwargs)
