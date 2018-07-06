# -*- coding: utf-8 -*-
#
from gevent import monkey

monkey.patch_all()

import gevent
import gevent.pool
import gevent.queue
import gevent.backdoor

import json
import time
import sys
import os
import django

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '../../edm_web')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edm_web.settings")
django.setup()

import urllib3
import logging
from django_redis import get_redis_connection
from django.conf import settings
from django.db import InterfaceError, DatabaseError, connections
from app.template.models import SendTemplate, TemplateCheckSetting, RefTemplate
from lib.template import MulTemplateEmail

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)s %(message)s'))

log = logging.getLogger('incheck')
log.addHandler(_handler)
log.setLevel(logging.DEBUG)

redis = get_redis_connection()
template_check_url = settings.TEMPLATE_CHECK_URL
http = urllib3.PoolManager(100, timeout=urllib3.Timeout(connect=10, read=300))
check_settings = {}

spam_note_dict = {
    'sender_blacklist': u'邮件模板被 U-Mail 反垃圾引擎综合评分判为垃圾邮件，详情见页面下方备注说明！',
    'subject_blacklist': u'邮件模板被 U-Mail 反垃圾引擎综合评分判为垃圾邮件，详情见页面下方备注说明！',
    'content_blacklist': u'邮件模板被 U-Mail 反垃圾引擎综合评分判为垃圾邮件，详情见页面下方备注说明！',
    'attachment_blacklist': u'邮件模板被 U-Mail 反垃圾引擎综合评分判为垃圾邮件，详情见页面下方备注说明！',

    'dspam': u'邮件模板被 Dspam 垃圾引擎判为垃圾邮件，详情见页面下方备注说明！',
    # 'ctasd': u'邮件模板被 Cyber 垃圾引擎判为垃圾邮件，详情见页面下方备注说明！'
}


def check_routine():
    while True:
        _, tpl_id = redis.brpop('template_check')
        pool.spawn(check, tpl_id)


def check(tpl_id):
    tpl = SendTemplate.objects.filter(id=tpl_id).first()
    if tpl is None:
        return
    for _ in xrange(5):
        try:
            t0 = time.time()
            r = http.request('POST', template_check_url,
                             fields={'sender': '', 'receiver': '', 'message': tpl.organize_msg(replace=True, mail_from="abc123xzy@bestedm.org")})
            t1 = time.time()
            if r.status == 200:
                j = json.loads(r.data)
                j['tpl_id'] = tpl_id
                redis.lpush('template_checked', json.dumps(j))
                log.info(u'check tpl_id={} success, time={:.1f}'.format(tpl_id, t1 - t0))
                return
            else:
                log.warning(u'check tpl_id={} failed, time={:.1f}'.format(tpl_id, t1 - t0))
        except BaseException:
            log.warning(u'check: exception, tpl_id={}'.format(tpl_id), exc_info=1)
        gevent.sleep(60)


def result_routine():
    for res in reversed(redis.lrange('template_checked_waiting', 0, -1)):
        save(res)
        redis.lrem('template_checked_waiting', 0, res)
    while True:
        res = redis.brpoplpush('template_checked', 'template_checked_waiting')
        save(res)
        redis.lrem('template_checked_waiting', 0, res)


def get_score_color(score):
    for k, v in check_settings.iteritems():
        if v['min'] <= score <= v['max']:
            return k
    assert 0


def save(res):
    r = json.loads(res)
    tpl_id = r['tpl_id']
    while True:
        try:
            tpl = SendTemplate.objects.filter(id=tpl_id).first()
            if tpl is None:
                log.info(u'save skipped, tpl_id={}'.format(tpl_id))
                return
            tpl.report = res
            tpl.edm_check_result = None
            if r['result'] == 'spam' and 'smtp' in r:
                tpl.edm_check_result = ','.join(str(i['id']) for i in r['smtp'])
            if r['result'] == 'spam' and len(r['reason']) > 0:
                tpl.result = 'red'
                tpl.spam_note = spam_note_dict.get(r['reason'], u'')
            elif r['result'] == 'spam' and 'ctasd' in r and not tpl.user.service().is_allow_cy_tpl:
                tpl.result = 'red'
                tpl.spam_note = u'邮件模板被 Cyber 垃圾引擎判为垃圾邮件，详情见页面下方备注说明！'
            # elif r['result'] == 'spam' and 'smtp' in r:
            #     tpl.edm_check_result = ','.join(str(i['id']) for i in r['smtp'])
            #     if tpl.user.service().is_allow_red_tpl:
            #         score_color = get_score_color(r['advance']['total_score'])
            #         if score_color == 'red':
            #             tpl.result = 'red'
            #             tpl.spam_note = u'邮件模板被 U-Mail 反垃圾引擎综合评分判为垃圾邮件，详情见页面下方备注说明！'
            #         else:
            #             tpl.result = 'red_pass'
            #             tpl.spam_note = '\n'.join(i['note'] for i in r['smtp'])
            #     else:
            #         tpl.result = 'red'
            #         tpl.spam_note = '\n'.join(i['note'] for i in r['smtp'])
            elif r['result'] == 'spam' and 'advance' in r:
                tpl.result = get_score_color(r['advance']['total_score'])
                if tpl.result == 'green':
                    tpl.spam_note = u''
                else:
                    tpl.spam_note = u'邮件模板被 U-Mail 反垃圾引擎综合评分判为垃圾邮件，详情见页面下方备注说明！'
            else:
                tpl.result = 'green'
                tpl.spam_note = u''
            tpl.save(update_fields=['result', 'spam_note', 'report', 'edm_check_result'])
            log.info(u'save success, tpl_id={}, result={}, spam_note={}, detail={}'.format(
                tpl_id, tpl.result, tpl.spam_note, r))
            return
        except (DatabaseError, InterfaceError) as e:
            # 如果报数据库异常，关闭连接，重新处理任务
            log.warning(u'DatabaseError', exc_info=1)
            reconnect()
        except BaseException as e:
            log.warning(u'save exception, tpl_id={}, detail={}'.format(tpl_id, r), exc_info=1)
        gevent.sleep(60)


def reconnect():
    try:
        log.info('Restoring the Mysql Connection start')
        cursor = connections['mm-ms'].cursor()
        db = cursor.db
        # assert issubclass(db.__class__, BaseDatabaseWrapper)
        if db.connection is None or not db.is_usable():
            db.close_if_unusable_or_obsolete()
            with db.wrap_database_errors:
                db.connect()
            log.info('Restoring the Mysql Connection end')
            time.sleep(5)
    except Exception as e:
        log.warning('DB Connection error', exc_info=1)


def recheck():
    try:
        redis.delete('template_check')
        for id in SendTemplate.objects.filter(result__isnull=True, name__isnull=False).order_by('-created').values_list(
                'id', flat=True):
            redis.lpush('template_check', id)
    except:
        log.warning(u'recheck DatabaseError', exc_info=1)
        reconnect()

def recheck_routine():
    while True:
        recheck()
        gevent.sleep(24 * 60 * 60)

#############################################################
#每天自动用CY引擎检测一遍系统的参考模板，命中的模板自动删除或禁用

def ref_check(t):
    """
    参考模板检测
    :return:
    """
    id = t.id
    obj = MulTemplateEmail(content=t.content, subject=t.subject, attachment=[])
    for _ in xrange(5):
        try:
            t0 = time.time()
            r = http.request('POST', template_check_url,
                             fields={'sender': '', 'receiver': '',
                                     'message': obj.get_message()})
            t1 = time.time()
            if r.status == 200:
                j = json.loads(r.data)
                j['tpl_id'] = id
                redis.lpush('ref_template_checked', json.dumps(j))
                log.info(u'check ref template tpl_id={} success, time={:.1f}'.format(id, t1 - t0))
                return
            else:
                log.warning(u'check ref template tpl_id={} failed, time={:.1f}'.format(id, t1 - t0))
        except BaseException:
            log.warning(u'check ref template: exception, tpl_id={}'.format(id), exc_info=1)
        gevent.sleep(60)

def ref_check_routine():
    while True:
        for t in RefTemplate.objects.filter(status=1):
            ref_check(t)
        gevent.sleep(24 * 60 * 60)

def ref_result_routine():
    for res in reversed(redis.lrange('ref_template_checked_waiting', 0, -1)):
        ref_save(res)
        redis.lrem('ref_template_checked_waiting', 0, res)
    while True:
        res = redis.brpoplpush('ref_template_checked', 'ref_template_checked_waiting')
        ref_save(res)
        redis.lrem('ref_template_checked_waiting', 0, res)


def ref_save(res):
    r = json.loads(res)
    tpl_id = r['tpl_id']
    while True:
        try:
            tpl = RefTemplate.objects.filter(id=tpl_id).first()
            result = 'green'
            if tpl is None:
                log.info(u'save skipped, tpl_id={}'.format(tpl_id))
                return
            if r['result'] == 'spam' and (len(r['reason']) > 0 or 'ctasd' in r):
                result = 'red'
                tpl.status = 0
                tpl.save()
            log.info(u'save ref success, tpl_id={}, result={}, detail={}'.format(
                tpl_id, result, r))
            return
        except (DatabaseError, InterfaceError) as e:
            # 如果报数据库异常，关闭连接，重新处理任务
            log.warning(u'DatabaseError', exc_info=1)
            reconnect()
        except BaseException as e:
            log.warning(u'save exception, tpl_id={}, detail={}'.format(tpl_id, r), exc_info=1)
        gevent.sleep(60)


def init():
    try:
        global check_settings
        spam_grade_dict = {1: 'green', 2: 'yellow', 3: 'red'}
        for s in TemplateCheckSetting.objects.all():
            spam_grade = spam_grade_dict.get(s.spam_grade, '')
            if spam_grade:
                check_settings[spam_grade] = {'min': s.min, 'max': s.max}
                if spam_grade == 'green':
                    check_settings['green']['min'] = float('-Inf')
                elif spam_grade == 'red':
                    check_settings['red']['max'] = float('Inf')
    except:
        log.warning(u'init DatabaseError', exc_info=1)
        reconnect()


def init_routine():
    while True:
        init()
        gevent.sleep(5 * 60)


def main():
    global pool
    pool = gevent.pool.Pool(5)
    init()
    all_routine = [
        # gevent.spawn(gevent.backdoor.BackdoorServer(('localhost', 10004)).serve_forever),
        gevent.spawn(init_routine),
        gevent.spawn(recheck_routine),
        gevent.spawn(check_routine),
        gevent.spawn(result_routine),
        gevent.spawn(ref_check_routine),
        gevent.spawn(ref_result_routine),
    ]
    gevent.joinall(all_routine)


if __name__ == '__main__':
    main()
