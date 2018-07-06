# -*- coding: utf-8 -*-
#
import time
import random
from django.db import connections
from django.db.models import Q
from django.http import Http404
from django_redis import get_redis_connection
from app.core.models import Services, CustomerMailbox, CustomerDomain, CustomerDomainMailboxRel, CustomerTrackDomain
from app.address.models import MailList, TaskMailList
from app.address.utils.vars import get_addr_var_fields
from app.template.models import SendTemplate
from app.task.models import SendTask, SendTaskReplyto, SendTaskTpl
from app.task.models import HOUR_SPEED
from app.track.models import StatTask, StatError

######################################################
# 获取任务相关的服务状态
def get_user_service(request):
    try:
        svs_obj = Services.objects.get(customer=request.user)
        if svs_obj.is_share_flag in ('1', '2'):
            custQtyValid = svs_obj.qty_valid
            is_service_disabled = True if svs_obj.disabled == '1' else False
        if svs_obj.is_share_flag == '4':
            custQtyValid = request.user.parent.service().qty_valid
            is_service_disabled = True if request.user.parent.service().disabled == '1' else False
        if svs_obj.is_share_flag == '3':
            custQtyValid1 = request.user.parent.service().qty_valid
            custQtyValid2 = svs_obj.limit_qty
            custQtyValid = custQtyValid1 if custQtyValid1 < custQtyValid2 else custQtyValid2
            is_service_disabled = True if request.user.parent.service().disabled == '1' else False
    except:
        custQtyValid = 0
        is_service_disabled = False
    return custQtyValid, is_service_disabled


######################################################
# 获取 添加任务的初始化信息
def get_task_add_context(request):
    # 任务名称
    send_name = '{}-{}-{}'.format(time.strftime('%Y%m%d%H%M%S'), request.user.id, random.randint(10, 100))
    # 地址池
    maillist_objs = MailList.objects.filter(
        Q(customer=request.user) |  Q(sub_share_maillist__user=request.user)).filter(
        isvalid=True, is_smtp=False).order_by('-id')[:500]
    # maillist_objs = MailList.objects.filter(customer=request.user, isvalid=True, is_smtp=False).order_by('-id')[:300]
    # 获取域名
    domain_list = CustomerMailbox.objects.filter(
        customer=request.user, disabled='0').values_list('domain', flat=True).distinct()
    domain_objs = CustomerDomain.objects.filter(domain__in=list(domain_list), customer_id__in=[0, request.user.id])

    # 共享域名获取
    ctype = CustomerDomainMailboxRel.objects.get_content_type('domain')
    share_domain_ids = CustomerDomainMailboxRel.objects.filter(customer=request.user, content_type=ctype).values_list(
        'object_id', flat=True)
    share_domain_objs = CustomerDomain.objects.filter(customer=request.user.parent, id__in=share_domain_ids)

    # 获取跟踪域名
    track_domain_list = CustomerTrackDomain.objects.filter(customer=request.user).order_by('-id')
    track_domain = track_domain_list[0].domain if track_domain_list else None

    # 复制
    task_id = request.GET.get('task_id', '')
    task_obj = None
    if task_id:
        task_obj = SendTask.objects.filter(user=request.user, id=task_id).first()

    task_copy_template_ids = task_obj.get_copy_template_ids() if task_obj else []
    c_send_qty_type = 'all'
    c_send_qty = 0
    c_send_qty_start = 0
    c_send_domain = 'all'
    c_send_fullname = None
    c_send_replyto = None
    c_track_status = 0
    c_track_domain = None
    c_is_need_receipt = False
    # 发送速度
    c_hour_speed = 5000
    # AB 发送
    c_is_ab = False
    c_ab_appraise_qty = 5000
    c_ab_content_limit = 2
    c_send_maillist_ids = []
    if task_obj:
        if task_obj.send_maillist_id == 0:
            c_send_maillist_ids = TaskMailList.objects.filter(send=task_obj).values_list("maillist_id", flat=True)
        else:
            c_send_maillist_ids = [task_obj.send_maillist_id]
        c_send_qty = task_obj.send_qty
        c_send_qty_start = task_obj.send_qty_start
        if c_send_qty_start != 0:
            c_send_qty_type = 'limit'
            c_send_qty_start = c_send_qty_start if c_send_qty_start else 1
        if task_obj.send_acct_type == 'domain':
            c_send_domain = task_obj.send_acct_domain
        c_send_fullname = task_obj.send_fullname
        c_send_replyto = task_obj.send_replyto
        c_track_status = task_obj.track_status
        c_track_domain = task_obj.track_domain
        c_is_need_receipt = task_obj.is_need_receipt
        c_hour_speed = task_obj.hour_speed
        c_is_ab = task_obj.is_ab
        c_ab_appraise_qty = task_obj.ab_appraise_qty
        c_ab_content_limit = task_obj.ab_content_limit

    # 失败地址重发(拒绝投递重发)
    errtype = request.GET.get('errtype', '')
    status = request.GET.get('status', '')
    retry_flag = False
    if status == 'retry' and errtype == '5' and task_obj:
        if task_obj.send_maillist_id == 0:
            T_send_maillist_ids = list(TaskMailList.objects.filter(send=task_obj).values_list("maillist_id", flat=True))
        else:
            T_send_maillist_ids = [task_obj.send_maillist_id]
        if not T_send_maillist_ids:
            raise Http404

        retry_flag = True
        _mobj = MailList.objects.create(
            customer=request.user,
            subject=u'{}_失败重发'.format(task_obj.send_name)
        )
        c_send_maillist_id = _mobj.id
        stats = StatTask.objects.filter(
            customer=request.user, task_ident=task_obj.send_name).values_list(
            'id', flat=True)
        lists = StatError.objects.filter(
            customer=request.user, task_id__in=stats).filter(
            error_type='5').values_list(
            'recipient', flat=True).distinct()
        _mobj.count_real = len(lists)
        _mobj.save()
        created = time.strftime("%Y-%m-%d %H:%M:%S")
        res = [(c_send_maillist_id, r, created) for r in lists]
        sql = "INSERT INTO `mm-pool`.`ml_subscriber_{}` (list_id, address, created) VALUES (%s, %s, %s)".format(
            request.user.id)
        cr = connections['mm-pool'].cursor()
        cr.executemany(sql, res)

        var_lists = get_addr_var_fields(cr, request.user.id)
        select_var_str = ','.join(var_lists)
        update_var_str = ', '.join('t1.{0}=t2.{0}'.format(varT) for varT in var_lists)
        update_sql = """
        UPDATE ml_subscriber_{0} t1, (
          SELECT address, list_id, fullname, sex, birthday, phone, area, {3}
          FROM ml_subscriber_{0} WHERE list_id in ({1})
        ) t2
        SET t1.fullname=t2.fullname, t1.sex=t2.sex, t1.birthday=t2.birthday, t1.phone=t2.phone, t1.area=t2.area, {4}
        WHERE t1.address = t2.address AND t1.list_id={2};
        """.format(request.user.id, ",".join(map(str, T_send_maillist_ids)), c_send_maillist_id, select_var_str, update_var_str)
        cr.execute(update_sql)
        task_copy_template_ids = []
        c_send_maillist_ids = [c_send_maillist_id]

    # 指定地址
    replyto_obj, _c = SendTaskReplyto.objects.get_or_create(user=request.user)
    c_send_replyto = c_send_replyto if c_send_replyto else replyto_obj.send_replyto

    track_domain = c_track_domain if c_track_domain else track_domain
    template_ids = ','.join(map(str, task_copy_template_ids)) if task_copy_template_ids else request.GET.get(
        'template_ids', '')
    select_template_ids = []
    if template_ids:
        select_template_ids = map(int, template_ids.split(','))

    select_template_ids = task_copy_template_ids if task_copy_template_ids else select_template_ids

    # 加载模板
    template_existed_1, load_template_existed = False, True
    # lists = SendTemplate.objects.filter(user=request.user, isvalid=True, result__in=['green', 'yellow', 'red_pass'])
    lists = SendTemplate.objects.filter(
        Q(user=request.user) | Q(sub_share_template__user=request.user)).filter(
        isvalid=True, result__in=['green', 'yellow', 'red_pass'])
    template_lists = lists.filter(id__in=select_template_ids)
    if template_lists:
        template_existed_1 = True
    exclude_template_existed = lists.exclude(id__in=select_template_ids).exists()
    template_existed = True if ( template_existed_1 or exclude_template_existed ) else False

    # 获取测试通道数量
    redis = get_redis_connection()
    test_channal_qty = redis.hget('channel:cfg', 'qty') or 30
    context = {
        'send_name': send_name,
        'template_lists': template_lists,
        'maillist_objs': maillist_objs,

        'domain_objs': domain_objs,
        'share_domain_objs': share_domain_objs,

        'track_domain_list': track_domain_list,
        'track_domain': track_domain,
        # 'custQtyValid': custQtyValid,
        # 'is_service_disabled': is_service_disabled,

        'template_ids': template_ids,
        'template_existed': template_existed,
        'exclude_template_existed': exclude_template_existed,

        "c_send_maillist_ids": c_send_maillist_ids,
        'c_send_qty_type': c_send_qty_type,
        'c_send_qty': c_send_qty,
        'c_send_qty_start': c_send_qty_start,
        'c_send_domain': c_send_domain,
        'c_send_fullname': c_send_fullname,
        'c_send_replyto': c_send_replyto,
        'c_track_status': c_track_status,
        'c_is_need_receipt': c_is_need_receipt,

        'retry_flag': retry_flag,

        'test_channal_qty': test_channal_qty,
        # 发送速度
        "c_hour_speed": c_hour_speed,
        "hour_speeds":  HOUR_SPEED,
        # AB 发送
        "c_is_ab": c_is_ab,
        "c_ab_appraise_qty": c_ab_appraise_qty,
        "c_ab_content_limit": c_ab_content_limit,
    }
    return context


######################################################
# 获取 修改任务的初始化信息
def get_task_modify_context(request, task_id):
    # 地址池
    # maillist_objs = MailList.objects.filter(customer=request.user, is_smtp=False, isvalid=True)[:300]
    maillist_objs = MailList.objects.filter(
        Q(customer=request.user) |  Q(sub_share_maillist__user=request.user)).filter(
        isvalid=True, is_smtp=False).order_by('-id')[:500]
    # 加载模板
    select_template_ids = SendTaskTpl.objects.filter(task_id=task_id).values_list('template_id', flat=True)
    template_existed_1, load_template_existed = False, True
    template_ids_str = ''
    if select_template_ids:
        template_ids_str = ','.join(map(str, select_template_ids))
    lists = SendTemplate.objects.filter(
        Q(user=request.user) | Q(sub_share_template__user=request.user)).filter(
        result__in=['green', 'yellow', 'red_pass']).filter(isvalid=True)
    template_lists = lists.filter(id__in=select_template_ids)
    if template_lists:
        template_existed_1 = True
    exclude_template_existed = lists.exclude(id__in=select_template_ids).exists()
    template_existed = True if ( template_existed_1 or exclude_template_existed ) else False

    # 获取域名
    domain_list = CustomerMailbox.objects.filter(
        customer=request.user, disabled='0').values_list('domain', flat=True).distinct()
    domain_objs = CustomerDomain.objects.filter(domain__in=list(domain_list), customer_id__in=[0, request.user.id])
    # domain_objs = CustomerDomain.objects.filter(customer=request.user, status='Y')

    # 共享域名获取
    ctype = CustomerDomainMailboxRel.objects.get_content_type('domain')
    share_domain_ids = CustomerDomainMailboxRel.objects.filter(customer=request.user, content_type=ctype).values_list(
        'object_id', flat=True)
    share_domain_objs = CustomerDomain.objects.filter(customer=request.user.parent, id__in=share_domain_ids)

    # 获取跟踪域名
    track_domain_list = CustomerTrackDomain.objects.filter(customer=request.user).order_by('-id')
    context = {
        # 'task_obj': obj,
        'maillist_objs': maillist_objs,
        'domain_objs': domain_objs,
        'share_domain_objs': share_domain_objs,
        # 'c_send_maillist_ids': task_tools.get_modify_maillistid(obj),

        'track_domain_list': track_domain_list,
        # 'custQtyValid': custQtyValid,
        # 'is_service_disabled': is_service_disabled,


        'template_lists': template_lists,
        'template_ids': select_template_ids,
        'template_existed': template_existed,
        'exclude_template_existed': exclude_template_existed,
        'template_ids_str': template_ids_str,

        # 发送速度
        "hour_speeds":  HOUR_SPEED,
    }
    return context

