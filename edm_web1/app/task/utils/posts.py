# -*- coding: utf-8 -*-
#
import json
from django.contrib import messages
from django.http import HttpResponseRedirect
from django_redis import get_redis_connection
from django.utils.translation import ugettext_lazy as _
from app.core.models import CustomerTrackDomain
from app.address.models import MailList, TaskMailList
from app.template.models import SendTemplate
from app.task.models import SendTask, SendTaskReplyto, SendTaskTpl, SendContent
from app.trigger.models import Trigger, TriggerListShip, TriggerSendtaskShip
from app.task.utils import tools as task_tools
from app.template.utils import templates
from app.address.utils import addresses as model_addresses
from app.utils.redislock import simple_acquire_lock, simple_realese_lock


def get_verify_status(customer, real_send_qty):
    """
    判断任务是否需要审核
    :param customer: 客户对象
    :param real_send_qty: 实际发送数量
    :return:
    """
    # 客户服务类
    srv = customer.service()
    is_verify = srv.is_verify
    verify_status = '0' if is_verify == '1' else '1'
    is_test_account = srv.server_type in ['1', '2', '6']
    # 获取测试通道数量
    redis = get_redis_connection()
    test_channal_qty = redis.hget('channel:cfg', 'qty') or 30
    # 如果发送数超过 100000 ，必须人工审核
    if real_send_qty >= 100000:
        verify_status = '0'
    elif real_send_qty <= int(test_channal_qty):
        verify_status = '0' if is_test_account else '1'
    return verify_status


# 任务添加提交
def post_task_add(request, is_service_disabled):
    if is_service_disabled:
        messages.add_message(request, messages.ERROR, _(u'修改任务失败；该账户已禁止发送任务，请联系您的客服！'))
        return HttpResponseRedirect('/task/?isvalid=1')

    data = request.POST
    user = request.user
    send_name = data.get('send_name', '')
    redis = get_redis_connection()
    send_name_lock_key = ":edmweb:sendtask:sendname:lock:{}".format(send_name)
    if simple_acquire_lock(redis, send_name_lock_key, 120):
        messages.add_message(request, messages.SUCCESS, _(u'任务%(send_name)s添加成功')% {'send_name': send_name})
        return HttpResponseRedirect('/task/?isvalid=1')

    track_status = data.get('track_status', '')
    track_domain = data.get('track_domain', '')
    send_domain = data.get('send_domain', '')
    send_account = data.get('send_account', '')
    send_qty_remark = data.get('send_addr_count', '')
    is_need_receipt = int(data.get('is_need_receipt', '0'))

    hour_speed = data.get('hour_speed', '')
    try:
        hour_speed = hour_speed and int(hour_speed) or 0
    except:
        hour_speed=0

    # AB
    is_ab = data.get('is_ab', 'off')
    ab_appraise_qty = data.get('ab_appraise_qty', '0')
    ab_content_limit = data.get('ab_content_limit', '0')
    is_ab = True if is_ab=='on' else False

    if send_domain == 'all':
        send_acct_type = 'all'
    elif send_domain != 'all' and send_account == 'all':
        send_acct_type = 'domain'
    else:
        send_acct_type = 'address'
    send_acct_domain = send_domain
    send_acct_address = send_account

    send_replyto = data.get('send_replyto', '')
    send_fullname = data.get('send_fullname', '')
    # send_maillist_id = int(data.get('send_maillist', ''))
    send_maillist_ids = data.getlist('send_maillist', '')
    # 兼容历史
    send_maillist_id = 0
    send_maillist = ""

    template_ids = data.getlist('template', '')
    send_qty_type = data.get('send_qty_type', '')
    send_qty = data.get('send_qty', 0)
    send_qty_start = data.get('send_qty_start', 0)
    if send_qty_type == 'limit' and send_qty:
        send_qty, send_qty_start = send_qty, send_qty_start
    else:
        send_qty, send_qty_start = 0, 0
    if send_maillist_ids and len(send_maillist_ids)>=2:
        send_qty, send_qty_start = 0, 0

    send_date = data.get('send_date', '')
    send_time = send_date if send_date else None
    send_status = int(data.get('send_status', ''))

    # verify_status = 0 if request.user.service().is_verify == '1' else 1
    # 更新跟踪域名
    _existed = CustomerTrackDomain.objects.filter(customer=request.user, domain=track_domain).exists()
    if not _existed and track_domain:
        CustomerTrackDomain.objects.create(
            customer=request.user,
            domain=track_domain
        )

    # 保存指定回复地址
    replyto_obj, _c = SendTaskReplyto.objects.get_or_create(user=request.user)
    replyto_obj.send_replyto = send_replyto
    replyto_obj.save()
    # 保存任务
    obj = SendTask(user=user, send_name=send_name, send_acct_type=send_acct_type, send_acct_domain=send_acct_domain,
                   send_acct_address=send_acct_address,
                   send_replyto=send_replyto, send_fullname=send_fullname, send_maillist=send_maillist,
                   send_maillist_id=send_maillist_id,
                   send_qty=send_qty, send_qty_remark=send_qty_remark, send_qty_start=send_qty_start,
                   send_time=send_time, send_status=send_status,
                   track_status=track_status, track_domain=track_domain, is_need_receipt=is_need_receipt,
                   hour_speed=hour_speed,
                   is_ab=is_ab, ab_appraise_qty=ab_appraise_qty, ab_content_limit=ab_content_limit
                   )

    verify_status = get_verify_status(request.user, obj.get_real_send_qty())
    if verify_status == '0' and send_status == 2:
        obj.send_status = 1
    # elif maillist_obj.is_importing:
    #     obj.send_status = -5
    obj.verify_status = verify_status
    obj.save()
    task_id = obj.id
    SendContent.objects.filter(send_id=task_id).update(isvalid=False)
    for template_id in template_ids:
        if not templates.check_temlates_exists_pc(request, template_id): continue
        SendTaskTpl.objects.get_or_create(task_id=task_id, template_id=template_id)
        content_id = task_tools.organize_msg(task_id, template_id, user, send_replyto, None, is_need_receipt,
                                             track_domain)
        redis.lpush('edm_web_mail_content_point_queue', json.dumps({
            "user_id": user.id,
            'content_id': content_id,
            'track_status': int(track_status),
            'is_need_receipt': is_need_receipt,
            'track_domain': track_domain,
            'task_ident': send_name,
            'send_maillist_id': None,
        }))

    # 关联地址池
    TaskMailList.objects.filter(send_id=task_id).delete()
    for list_id in send_maillist_ids:
        list_customer_id = model_addresses.get_address_userid(request, list_id)
        if not list_customer_id: continue
        # mailistobj = MailList.objects.filter(id=list_id, customer=request.user).first()
        # if not mailistobj: continue
        TaskMailList.objects.get_or_create(send_id=task_id, maillist_id=list_id)
        # 地址池推送检测
        redis.lpush("zhimeng:qq:check:queue", "{}_{}".format(list_customer_id, list_id))
    # 关联触发器保存
    triggerList = data.getlist("trigger[]", "")
    TriggerSendtaskShip.objects.filter(task_id=task_id).delete()
    bulkTrig = []
    for trigger_id in triggerList:
        bulkTrig.append( TriggerSendtaskShip(task_id=task_id, trigger_id=trigger_id) )
    if bulkTrig:
        TriggerSendtaskShip.objects.bulk_create(bulkTrig)
    if send_status == 2 and verify_status == '1':
        obj.start()

    # messages.add_message(request, messages.SUCCESS, _(u'任务添加成功'))
    messages.add_message(request, messages.SUCCESS, _(u'任务%(send_name)s添加成功') % {'send_name': send_name})
    return HttpResponseRedirect('/task/?isvalid=1')


# 任务修改提交
def post_task_modify(request, task_id, is_service_disabled):
    if is_service_disabled:
        messages.add_message(request, messages.ERROR, _(u'修改任务失败；该账户已禁止发送任务，请联系您的客服！'))
        return HttpResponseRedirect('/task/?isvalid=1')

    data = request.POST
    user = request.user
    send_name = data.get('send_name', '')
    track_status = data.get('track_status', '')
    track_domain = data.get('track_domain', '')
    send_domain = data.get('send_domain', '')
    send_account = data.get('send_account', '')
    send_qty_remark = data.get('send_addr_count', '')
    is_need_receipt = int(data.get('is_need_receipt', '0'))

    hour_speed = data.get('hour_speed', '')
    try:
        hour_speed = hour_speed and int(hour_speed) or 0
    except:
        hour_speed=0

    # AB
    is_ab = data.get('is_ab', 'off')
    ab_appraise_qty = data.get('ab_appraise_qty', '0')
    ab_content_limit = data.get('ab_content_limit', '0')
    is_ab = True if is_ab=='on' else False

    if send_domain == 'all':
        send_acct_type = 'all'
    elif send_domain != 'all' and send_account == 'all':
        send_acct_type = 'domain'
    else:
        send_acct_type = 'address'
    send_acct_domain = send_domain
    send_acct_address = send_account

    send_replyto = data.get('send_replyto', '')
    send_fullname = data.get('send_fullname', '')

    send_maillist_ids = data.getlist('send_maillist', '')
    # 兼容历史
    send_maillist_id = 0
    send_maillist = ""

    template_ids = data.getlist('template', '')

    send_qty_type = data.get('send_qty_type', '')
    send_qty = data.get('send_qty', 0)
    send_qty_start = data.get('send_qty_start', 0)
    if send_qty_type == 'limit' and send_qty:
        send_qty, send_qty_start = send_qty, send_qty_start
    else:
        send_qty, send_qty_start = 0, 0

    if send_maillist_ids and len(send_maillist_ids)>=2:
        send_qty, send_qty_start = 0, 0

    send_date = data.get('send_date', '')
    send_status = int(data.get('send_status', ''))
    send_time = send_date if send_date else None

    SendTaskTpl.objects.filter(task_id=task_id).delete()
    tasks = SendTask.objects.filter(id=task_id)
    verify_status = get_verify_status(request.user, tasks[0].get_real_send_qty())
    if verify_status == '0' and send_status == 2:
        send_status = 1

    # 保存指定回复地址
    replyto_obj = SendTaskReplyto.objects.filter(user=request.user).first()
    if replyto_obj:
        replyto_obj.send_replyto = send_replyto
        replyto_obj.save()

    # 更新跟踪域名
    _existed = CustomerTrackDomain.objects.filter(customer=request.user, domain=track_domain).exists()
    if not _existed and track_domain:
        CustomerTrackDomain.objects.create(
            customer=request.user,
            domain=track_domain
        )

    # tasks.update( user=user, send_name=send_name, send_acct_type=send_acct_type, send_acct_domain=send_acct_domain, send_acct_address=send_acct_address,
    # send_replyto=send_replyto, send_fullname=send_fullname, send_maillist=send_maillist, send_maillist_id=send_maillist_id,
    # send_qty=send_qty, send_qty_remark=send_qty, send_qty_start=send_qty_start,
    #               send_time=send_time, send_status=send_status, verify_status=verify_status,
    #               time_start=time_start, time_end=time_end, track_status=track_status, track_domain=track_domain )
    if verify_status == '0' or send_status == 1:
        tasks.update(
            user=user, send_name=send_name, send_acct_type=send_acct_type, send_acct_domain=send_acct_domain,
            send_acct_address=send_acct_address,
            send_replyto=send_replyto, send_fullname=send_fullname,
            send_time=send_time, send_status=send_status, verify_status=verify_status,
            track_status=track_status, track_domain=track_domain,

            send_maillist=send_maillist, send_maillist_id=send_maillist_id,
            send_qty=send_qty, send_qty_remark=send_qty_remark, send_qty_start=send_qty_start,
            is_need_receipt=is_need_receipt, hour_speed=hour_speed,
            is_ab=is_ab, ab_appraise_qty=ab_appraise_qty, ab_content_limit=ab_content_limit
        )
    else:
        tasks.update(
            user=user, send_name=send_name, send_acct_type=send_acct_type, send_acct_domain=send_acct_domain,
            send_acct_address=send_acct_address,
            send_replyto=send_replyto, send_fullname=send_fullname,
            send_time=send_time, send_status=send_status, verify_status=verify_status,
            track_status=track_status, track_domain=track_domain,
            is_need_receipt=is_need_receipt, hour_speed=hour_speed,
            is_ab=is_ab, ab_appraise_qty=ab_appraise_qty, ab_content_limit=ab_content_limit
        )
    SendContent.objects.filter(send_id=task_id).update(isvalid=False)
    redis = get_redis_connection()
    for template_id in template_ids:
        if not templates.check_temlates_exists_pc(request, template_id): continue
        SendTaskTpl.objects.get_or_create(task_id=task_id, template_id=template_id)
        content_id = task_tools.organize_msg(task_id, template_id, user, send_replyto,
                                             None, is_need_receipt, track_domain)
        redis.lpush('edm_web_mail_content_point_queue', json.dumps({
            "user_id": user.id,
            'content_id': content_id,
            'track_status': int(track_status),
            'is_need_receipt': is_need_receipt,
            'track_domain': track_domain,
            'task_ident': send_name,
            'send_maillist_id': None,
        }))
    if verify_status == '0' or send_status == 1:
        # 关联地址池
        TaskMailList.objects.filter(send_id=task_id).delete()
        for list_id in send_maillist_ids:
            list_customer_id = model_addresses.get_address_userid(request, list_id)
            if not list_customer_id: continue
            # mailistobj = MailList.objects.filter(id=list_id, customer=request.user).first()
            # if not mailistobj: continue
            TaskMailList.objects.get_or_create(send_id=task_id, maillist_id=list_id)
            # 地址池推送检测
            redis.lpush("zhimeng:qq:check:queue", "{}_{}".format(list_customer_id, list_id))
        # if send_maillist_ids:
        #     # 关联地址池
        #     TaskMailList.objects.filter(send_id=task_id).delete()
        #     for list_id in send_maillist_ids:
        #         mailistobj = MailList.objects.filter(id=list_id, customer=request.user).first()
        #         if not mailistobj: continue
        #         TaskMailList.objects.get_or_create(send_id=task_id, maillist_id=list_id)
        #         # 地址池推送检测
        #         redis.lpush("zhimeng:qq:check:queue", "{}_{}".format(user.id, list_id))

    # 关联触发器保存
    triggerList = data.getlist("trigger[]", "")
    TriggerSendtaskShip.objects.filter(task_id=task_id).delete()
    bulkTrig = []
    for trigger_id in triggerList:
        bulkTrig.append( TriggerSendtaskShip(task_id=task_id, trigger_id=trigger_id) )
    if bulkTrig:
        TriggerSendtaskShip.objects.bulk_create(bulkTrig)

    if send_status == 2 and verify_status == '1':
        tasks[0].start()

    messages.add_message(request, messages.SUCCESS, _(u'任务%(send_name)s修改成功') % {'send_name': send_name})
    # messages.add_message(request, messages.SUCCESS, _(u'任务修改成功'))
    return HttpResponseRedirect('/task/?isvalid=1')
