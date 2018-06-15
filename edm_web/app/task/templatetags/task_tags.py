# coding=utf-8
from django import template
from app.task.models import SendTaskTpl, SendTask
from app.address.models import MailList, TaskMailList
from app.template.models import SendTemplate
from django.template.defaultfilters import date as dateformat

from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.filter
def show_sender_type(obj):
    if obj.send_acct_type == 'all':
        return _(u'所有域名下的所有发件人')
    else:
        if obj.send_acct_address:
            send_acct_address = obj.send_acct_address
        else:
            send_acct_address = obj.send_account
        if send_acct_address == 'all':
            return _(u'单个域名( %(domain)s )下的所有发件人') % {'domain': obj.send_acct_domain}
        elif send_acct_address and obj.send_acct_domain:
            return _(u'单个域名( %(domain)s )下的单个发件人( %(address)s )') % {'domain': obj.send_acct_domain, 'address': send_acct_address}
        else:
            return u''

@register.assignment_tag
def ifinlist(key, list_str):
    return str(key) in list_str.split(',')

@register.filter
def show_isvalid(_bool):
    if _bool:
        return "1"
    else:
        return "2"


@register.assignment_tag
def get_maillist_subject(taskobj):
    if taskobj.send_maillist_id ==0:
        lists = TaskMailList.objects.filter(send=taskobj)
        if lists.count>=2:
            s = []
            for d in lists:
                try:
                    _s = d.maillist.subject
                except:
                    _s = _(u"未分类地址")
                s.append(_s)
            return s
        else:
            try:
                s = lists[0].maillist.subject
            except:
                s = _(u"未分类地址")
            return [s]
    else:
        s = taskobj.send_maillist and taskobj.send_maillist or _(u"未分类地址")
        return [s]

@register.assignment_tag
def get_maillist_canmodify(taskobj):
    if taskobj.send_maillist_id ==0:
        lists = TaskMailList.objects.filter(send=taskobj)
        if lists.count>=2:
            return True
        return False
    return False

@register.assignment_tag
def get_maillist_bysendname(customer_id, task_ident):
    if task_ident:
        obj = SendTask.objects.filter(user_id=customer_id, send_name=task_ident).first()
        if obj:
            if obj.send_maillist_id == 0:
                return [o.maillist.subject for o in obj.taskmaillist_set.all()]
            else:
                return [ obj.send_maillist ]
    return [""]
