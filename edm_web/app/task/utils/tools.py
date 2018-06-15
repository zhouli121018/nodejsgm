# -*- coding: utf-8 -*-
#
import random
from django.conf import settings
from django.http import Http404
from app.core.models import CustomerTrackDomain, SysPicDomain
from app.template.models import SendTemplate
from app.task.models import SendContent, SendTask
from app.address.models import TaskMailList

def get_modify_maillistid(obj):
    if obj.send_maillist_id ==0:
        lists = TaskMailList.objects.filter(send=obj)
        if lists.count>=2:
            s = []
            for d in lists:
                s.append(d.maillist_id)
            return s
        else:
            return lists and [ lists[0].maillist_id ]
    else:
        return [ obj.send_maillist_id ]

#####################################
# 任务 生成邮件内容
# 保存时将模板组织成邮件
def organize_msg(task_id=None, template_id=None, user=None, reply_to=None, send_maillist_id=None, is_need_receipt=None,
                  track_domain=None):
    if not track_domain:
        track_domain_lists = CustomerTrackDomain.objects.filter(customer=user, isdefault=True)
        if not track_domain_lists:
            track_domain_lists = CustomerTrackDomain.objects.filter(customer=user, isdefault=False)
        track_domain = random.choice(track_domain_lists).domain if track_domain_lists else ''
    obj = SendTemplate.objects.get(id=template_id)
    sys_track_domain = SysPicDomain.objects.filter(isvalid=True).values_list('domain', flat=True)
    if not sys_track_domain:
        sys_track_domain = settings.TEMPLATE_PIC_URLS
    message = obj.organize_msg(reply_to=reply_to, task_id=task_id, send_maillist_id=send_maillist_id,
                               is_need_receipt=is_need_receipt, track_domain=track_domain,
                               sys_track_domain=sys_track_domain)
    content_obj = SendContent.objects.create(
        send_id=task_id, template_id=template_id, user=user,
        send_content=message, template_name=obj.name,
        isvalid=True,
    )
    return content_obj.id


def get_task_obj(request, task_id):
    """ 检测模板是否在母账户中。
    """
    try:
        return SendTask.objects.get(id=task_id, user=request.user)
    except:
        try:
            obj = SendTask.objects.get(id=task_id)
            if obj.user.parent == request.user:
                return obj
            raise Http404
        except:
            raise Http404
