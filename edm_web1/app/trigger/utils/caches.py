# -*- coding: utf-8 -*-

import time
import random
from django.core.cache import cache
from app.task.models import SendTask
from app.trigger.models import Trigger, TriggerTask, TriggerTaskOne, TriggerAction, TriggerSendtaskShip
from app.core.models import Customer, CustomerDomain, CustomerMailbox, CustomerDomainMailboxRel

def getTriggerTask(trigger, task_obj):
    key = 'trigger_task:{}_{}_{}'.format(time.strftime("%Y%m%d"), trigger.id, task_obj.id)
    result = cache.get(key)
    if not result:
        result, _ = TriggerTask.objects.get_or_create(send_task=task_obj, trigger=trigger, customer=task_obj.user)
        cache.set(key, result, 300)
    return result

def getTriggerActions(task_ident):
    """
    根据task_ident 获取该任务的所有触发动作
    :param task_ident:
    :return:
    """
    key = 'trigger_action:{}'.format(task_ident)
    result = cache.get(key)
    if result is None:
        result = []
        task_obj = SendTask.objects.filter(send_name=task_ident).first()
        if task_obj and TriggerSendtaskShip.objects.filter(task=task_obj):
            result = TriggerAction.objects.filter(trigger__in=task_obj.trigger_set.filter(status='enable', type='open'), status='enable')
        cache.set(key, result, 300)
    return result


def retrunAccount(key, res):
    result = random.choice(res)
    cache.set(key, result, 600)
    return result

def getSmtpAcount(user_id, action_id, send_domain, send_addr):
    key = "trigger:task:account:{}:{}:{}:{}".format(user_id, action_id, send_domain, send_addr)
    result = cache.get(key)
    if not result and send_domain=="all":
        # 客户账号
        res = CustomerMailbox.objects.filter(customer_id=user_id, disabled='0')
        if res: return retrunAccount(key, res)
        # 共享账号
        ctype = CustomerDomainMailboxRel.objects.get_content_type('mailbox')
        box_ids = CustomerDomainMailboxRel.objects.filter(customer_id=user_id, content_type=ctype).values_list('object_id', flat=True)
        cobj = Customer.objects.get(id=user_id)
        domains = CustomerDomain.objects.filter(customer=cobj.parent).values_list('domain', flat=True)
        res = CustomerMailbox.objects.filter(
            customer=cobj.parent, domain__in=domains, disabled='0', id__in=box_ids
        ).exclude(mailbox__isnull=True)
        if res: return retrunAccount(key, res)
        return None
    elif not result and send_addr=="all":
        res = CustomerMailbox.objects.filter(customer_id=user_id, domain=send_domain, disabled='0')
        if res: return retrunAccount(key, res)
        # 共享账号
        ctype = CustomerDomainMailboxRel.objects.get_content_type('mailbox')
        box_ids = CustomerDomainMailboxRel.objects.filter(customer_id=user_id, content_type=ctype).values_list('object_id', flat=True)
        cobj = Customer.objects.get(id=user_id)
        res = CustomerMailbox.objects.filter(
            customer=cobj.parent, domain=send_domain, disabled='0', id__in=box_ids
        ).exclude(mailbox__isnull=True)
        if res: return retrunAccount(key, res)
        return None
    elif not result:
        res = CustomerMailbox.objects.filter(customer_id=user_id, domain=send_domain, disabled='0', mailbox=send_addr)
        if res: return retrunAccount(key, res)
        # 共享账号
        ctype = CustomerDomainMailboxRel.objects.get_content_type('mailbox')
        box_ids = CustomerDomainMailboxRel.objects.filter(customer_id=user_id, content_type=ctype).values_list('object_id', flat=True)
        cobj = Customer.objects.get(id=user_id)
        res = CustomerMailbox.objects.filter(
            customer=cobj.parent, domain=send_domain, disabled='0', mailbox=send_addr, id__in=box_ids
        ).exclude(mailbox__isnull=True)
        if res: return retrunAccount(key, res)
        return None
    return result