# -*- coding: utf-8 -*-
"""
定时每天跑一次
将当天需要启动的触发任务（节假日触发器和生日触发器）写入数据库中
"""
from gevent import monkey

monkey.patch_all()

import os
import sys
import gevent
import gevent.pool
import datetime
import django

web_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../edm_web'))
sys.path.append(web_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'edm_web.settings')
if django.VERSION >= (1, 7):
    django.setup()

from django.utils import timezone
from django_redis import get_redis_connection
from django.db import connection
from app.trigger.models import TriggerTask, TriggerTaskOne, TriggerAction
from app.trigger.utils import tools
from lib._signal import init_gevent_signal
from lib.log import getLogger

log = getLogger("TriggerCron", logfile='/home/log/edm_web/trigger_cron.log')
redis = get_redis_connection()

######################################################
# 节假日触发器
def holiday_trig():
    actions = TriggerAction.objects.filter(trigger__status='enable', trigger__type='holiday', status='enable')
    maillist_sql = 'SELECT `address` FROM `mm-pool`.`ml_subscriber_%s` WHERE list_id=%d'
    cursor = connection.cursor()
    for action in actions:
        action_time = datetime.datetime.combine(action.con_holiday_date, datetime.datetime.min.time()) + timezone.timedelta(minutes=action.t_action_time)
        print action.id, action_time
        if action_time.date() == datetime.date.today():
            trigger = action.trigger
            maillist_ids = trigger.get_maillist_ids()
            trigger_task, _ = TriggerTask.objects.get_or_create(trigger=trigger, customer=trigger.customer)
            i = 0
            obj_lists = []
            log.info(u'[Holiday]: action({}{})'.format(action, action.id))
            for m_id in maillist_ids:
                cursor.execute(maillist_sql % (trigger.customer_id, m_id))
                for email, in cursor.fetchall():
                    if tools.existsTriggerAcionOne(trigger_task, action, email):
                        log.warning(u"[Trig:Holiday:Exist] email: {}, action: {}".format(email, action.id))
                        continue
                    obj = TriggerTaskOne(
                        trigger_task=trigger_task, trigger_action=action,
                        email=email, action_time=action_time)
                    obj_lists.append(obj)
                    if i >= 10000:
                        TriggerTaskOne.objects.bulk_create(obj_lists)
                        obj_lists = []
                        i = 0
                TriggerTaskOne.objects.bulk_create(obj_lists)
    cursor.close()

def birthday_trig():
    actions = TriggerAction.objects.filter(trigger__status='enable', trigger__type='birthday', status='enable')
    cursor = connection.cursor()
    maillist_sql = "SELECT `address` FROM `mm-pool`.`ml_subscriber_%s` WHERE list_id=%d and DATE_FORMAT(`birthday`,'%s') = '%s'"
    for action in actions:
        birthday_time = datetime.datetime.now() - timezone.timedelta(minutes=action.t_action_time)
        action_time = datetime.datetime.combine(birthday_time.date(), datetime.datetime.min.time()) + timezone.timedelta(minutes=action.t_action_time)

        trigger = action.trigger
        maillist_ids = trigger.get_maillist_ids()
        trigger_task, _ = TriggerTask.objects.get_or_create(trigger=trigger, customer=trigger.customer)
        i = 0
        obj_lists = []
        for m_id in maillist_ids:
            sql = maillist_sql % (trigger.customer_id, m_id, '%m-%d', birthday_time.strftime('%m-%d'))
            log.info(sql)
            cursor.execute(sql)

            for email, in cursor.fetchall():
                if tools.existsTriggerAcionOne(trigger_task, action, email):
                    log.warning(u"[Trig:Holiday:Exist] email: {}, action: {}".format(email, action.id))
                    continue
                obj = TriggerTaskOne(
                    trigger_task=trigger_task, trigger_action=action,
                    email=email, action_time=action_time)
                obj_lists.append(obj)
                if i >= 10000:
                    TriggerTaskOne.objects.bulk_create(obj_lists)
                    obj_lists = []
                    i = 0
            TriggerTaskOne.objects.bulk_create(obj_lists)
    cursor.close()

def main():
    global routines
    routines = [
        # gevent.spawn(gevent.backdoor.BackdoorServer(('localhost', 10004)).serve_forever),
        gevent.spawn(holiday_trig),
        gevent.spawn(birthday_trig),
    ]
    gevent.joinall(routines)


if __name__ == "__main__":
    log.info(u'program start...')
    main()
    log.info(u"program quit...")
