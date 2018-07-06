# -*- coding: utf-8 -*-
"""
触发器动作
"""
from gevent import monkey

monkey.patch_all()

import os
import sys
import gevent
import gevent.pool
import traceback
import json
import django

web_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../edm_web'))
sys.path.append(web_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'edm_web.settings')
if django.VERSION >= (1, 7):
    django.setup()

from django.utils import timezone
from django_redis import get_redis_connection
from django.db import InterfaceError, DatabaseError
from app.task.models import SendTask
from app.trigger.models import Trigger, TriggerTask, TriggerTaskOne, TriggerAction
from app.trigger.utils import caches
from app.trigger.utils import tools
from app.trigger.utils import orgemail
from app.trigger.utils.smtp import smtpSendEmail
from lib._signal import init_gevent_signal
from lib.dbreconnect import reconnectDB
from lib.log import getLogger

log = getLogger("Trigger")
redis = get_redis_connection()
signal_stop = False


######################################################
# 任务触发器
def _trigtask(data):
    ctime, task_ident, email, link, agent_info = json.loads(data)[:5]
    # log.info(u"[Trig:Task] task_ident: {}, email: {}, link: {}".format(task_ident, email, link))
    actions = caches.getTriggerActions(task_ident)
    if actions:
        log.info(u"[Trig:Task] task_ident: {}, email: {}, link: {}".format(task_ident, email, link))
        task_obj = SendTask.objects.get(send_name=task_ident)
        for action in actions:
            trigger_task = caches.getTriggerTask(action.trigger, task_obj)
            action_time = timezone.now() + timezone.timedelta(minutes=action.t_action_time)
            # 检测当前邮件的动作任务是否存在
            if tools.existsTriggerAcionOne(trigger_task, action, email):
                log.warning(u"[Trig:Task] task_ident: {}, email: {}, link: {}, action exist.".format(task_ident, email, link))
                continue
            condition = action.condition
            cond_url = action.con_url
            if ((condition == 'open')  # 打开
                    or (condition == 'click' and not cond_url)  # 点击 没有url
                    or (condition == 'click' and cond_url and link.find(cond_url) != -1)  # 点击 匹配到该url
                    or (condition == 'unsubscribe' and tools.isUnsubscribeUrl(link))):  # 退订链接
                log.info(
                    u"[Trig:Task] task_ident: {}, email: {}, link: {}, condition: {}, condurl: {}, success.".format(
                        task_ident, email, link, condition, cond_url))
                TriggerTaskOne.objects.create(
                    trigger_task=trigger_task, trigger_action=action,
                    email=email, action_time=action_time)


def trigtask():
    """ 任务发送相关触发动作
    触发动作： 打开；点击； 退订。
    """
    key = "trigger_waiting"
    while True:
        if signal_stop: break
        res = redis.brpop(key, timeout=5)
        if not res: continue
        _, d = res
        try:
            _trigtask(d)
        except (DatabaseError, InterfaceError), e:
            log.error(traceback.format_exc())
            redis.rpush(key, d)
            reconnectDB("mm-ms")
        except BaseException as e:
            log.error(traceback.format_exc())


######################################################
# 执行 触发任务
def trigtaskaction():
    key = "trigger:task:send"
    while True:
        if signal_stop: break
        try:
            lists = TriggerTaskOne.objects.filter(status='wait', action_time__lte=timezone.now())
            for obj in lists:
                if signal_stop: break
                obj.saveStatus("doing")
                redis.lpush(key, obj.id)
        except (DatabaseError, InterfaceError), e:
            log.error(traceback.format_exc())
            reconnectDB("mm-ms")
        except BaseException as e:
            log.error(traceback.format_exc())
        gevent.sleep(30)


######################################################
# 发送处理
def _trigtasksend(action_id):
    obj = TriggerTaskOne.objects.filter(id=action_id, status='doing').first()
    email = obj.email
    act_obj = obj.trigger_action
    tpl_obj = act_obj.template
    log.info(u"[Trig:Task:Send] action_id: {}, email: {}".format(action_id, email))
    if not tpl_obj:
        obj.saveStatus()
        log.error(u"[Trig:Task:Send] action_id: {}, email: {}, no template send".format(action_id, email))
        return
    user_id = tpl_obj.user_id
    attachment = tpl_obj.SendTemplate01.filter(attachtype='common').values_list('filepath', 'filetype', 'filename')
    send_acct_domain = act_obj.send_acct_domain
    send_acct_address = act_obj.send_acct_address
    track_domain = "count.bestedm.org"
    box_obj = caches.getSmtpAcount(user_id, action_id, send_acct_domain, send_acct_address)
    if not box_obj:
        obj.saveStatus()
        log.error(u"[Trig:Task:Send] action_id: {}, email: {}, no mailbox query".format(action_id, email))
        return
    msg = orgemail.OrgMessage(
        content_type=tpl_obj.content_type, character=tpl_obj.character, encoding=tpl_obj.encoding,
        user_id=user_id, template_id=tpl_obj.id,
        subject=tpl_obj.subject, content=tpl_obj.content, text_content=tpl_obj.text_content,
        edm_check_result=tpl_obj.edm_check_result,
        attachment=attachment,
        task_id=obj.trigger_task.id, send_maillist_id=None, task_ident=obj.trigger_task.name,
        mail_from=box_obj.mailbox, mail_to=email, reply_to=act_obj.replyto,
        is_need_receipt=False, track_domain=track_domain
    )()
    code, msg = smtpSendEmail(
        host="127.0.0.1", port=25,
        account=box_obj.mailbox, password=box_obj.password, sender=box_obj.mailbox, receivers=[obj.email], message=msg
    )
    obj.saveStatus()
    if code == -1:
        log.error(u"[Trig:Task:Send] action_id: {}, email: {}, code: {}, msg: {}".format(action_id, email, code, msg))


def trigtasksend():
    key = "trigger:task:send"
    while True:
        if signal_stop: break
        res = redis.brpop(key, timeout=5)
        if not res: continue
        _, action_id = res
        try:
            _trigtasksend(action_id)
        except (DatabaseError, InterfaceError), e:
            log.error(traceback.format_exc())
            redis.rpush(key, action_id)
            reconnectDB("mm-ms")
        except BaseException as e:
            log.error(traceback.format_exc())


######################################################
# 信号量处理
def signal_handle(mode):
    log.info(u"Catch signal: %s" % mode)
    global signal_stop
    signal_stop = True


def main():
    global routines
    init_gevent_signal(signal_handle)
    routines = [
        # gevent.spawn(gevent.backdoor.BackdoorServer(('localhost', 10004)).serve_forever),
        # 建立
        gevent.spawn(trigtask),
        gevent.spawn(trigtask),
        gevent.spawn(trigtask),
        gevent.spawn(trigtask),
        gevent.spawn(trigtask),
        # 启动
        gevent.spawn(trigtaskaction),
        # 发送
        gevent.spawn(trigtasksend),
        gevent.spawn(trigtasksend),
        gevent.spawn(trigtasksend),
        gevent.spawn(trigtasksend),
        gevent.spawn(trigtasksend),
    ]
    gevent.joinall(routines)


if __name__ == "__main__":
    log.info(u'program start...')
    main()
    log.info(u"program quit...")
