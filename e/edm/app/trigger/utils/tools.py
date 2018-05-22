# -*- coding: utf-8 -*-

import urlparse
from django.shortcuts import reverse
from app.trigger.models import TriggerTaskOne

def isUnsubscribeUrl(link):
    """
    http://pic.magvision.com/template/ajax_unsubscribe_or_complaints/?mailist={MAILLIST_ID}&recipents={RECIPIENTS}&mode=0
    ParseResult(scheme='http', netloc='pic.magvision.com', path='/template/ajax_unsubscribe_or_complaints/', params='', query='mailist={MAILLIST_ID}&recipents={RECIPIENTS}&mode=0', fragment='')
    {'mailist': ['{MAILLIST_ID}'], 'mode': ['0'], 'recipents': ['{RECIPIENTS}']}
    """
    uri = reverse("ajax_unsubscribe_or_complaints")
    result = urlparse.urlparse(link)
    if result.path != uri:
        return False
    params = urlparse.parse_qs(result.query)
    if 'mode' in params and params['mode'][0] == "0":
        return True
    return False


# 检测 当前邮件的动作任务是否存在
def existsTriggerAcionOne(tigger_task, tigger_action, email):
    if TriggerTaskOne.objects.filter(trigger_task=tigger_task, trigger_action=tigger_action, email=email).exists():
        return True
    return False



