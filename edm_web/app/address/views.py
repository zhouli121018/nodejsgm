# coding=utf-8
# Create your views here.
import os

import re
import json
import time
import random
import pymongo

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.db import connections
from django.conf import settings
from django.template.defaultfilters import date as dateformat
from django.core.urlresolvers import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from wsgiref.util import FileWrapper
from django.db.models import F, QuerySet
from django.contrib.contenttypes.models import ContentType
from django_redis import get_redis_connection
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from tagging.models import Tag, TaggedItem
from app.address.models import MailList, AddressImportLog, ShareMailList
from app.address.forms import MailListForm
from app.track.templatetags.track_tags import show_click_date
from app.other.models import EmailOpenClick
from app.address.tools import check_qq_addr
from app.address.utils.merge import mergeMaillist, mergeNewMaillist
from app.address.utils.pagination import invalidView
from app.address.utils.vars import get_addr_var_fields, get_fields_args
from app.address.utils import sqls as address_sqls, addresses as model_addresses, tools as address_tools
from lib import validators
from lib.common import get_object
from lib.excel_response import ExcelResponse, FormatExcelResponse
from django.utils.translation import ugettext_lazy as _

mongo_cfg = {
    'host': settings.MONGO_HOST,
    'port': settings.MONGO_PORT,
    'username': settings.MONGO_USER,
    'dbname': settings.MONGO_DBNAME,
    'password': settings.MONGO_PWD,
}
# 统计客户地址池数量队列（python 专用）
EDM_WEB_USER_MAIL_IMPORT_COUNT_QUEUE = 'edm_web_user_mail_import_count_queue'
# 客户地址池去重队列
EDM_WEB_MAIL_DUPLICATE_QUEUE = 'edm_web_mail_duplicate_queue'
# 地址池合并后去重操作队列
EMD_WEB_MAIL_MERGE_QUEUE = 'edm_web_mail_merge_queue'
# 用户地址池为0的地址数量
EDM_WEB_LIST_ZERO_COUNT_HASH = 'edm_web_list_zero_count_hash'
# 收集QQ地址
GLB_REDIS_REMOTE_GET_QQ = "edm_web_qq_check_queue"

# #### 联系人分类管理 #####
@login_required
def ml_maillist(request):
    isvalid = request.GET.get('isvalid', '')
    if request.method == "POST":
        cr = connections['mm-pool'].cursor()
        tablename = 'ml_subscriber_' + str(request.user.id)
        id = request.POST.get('id', False)
        ids_str = request.POST.get('ids', False)
        status = int(request.POST.get('status', False))
        id_del = int(request.POST.get('id_del', '0'))
        if int(status) == -3:  # 恢复地址池
            obj = get_object(MailList, request.user, id)
            obj.isvalid = True
            obj.save()
            messages.add_message(request, messages.SUCCESS, _(u'恢复地址池（%(subject)s)成功') % {"subject": obj.subject})
        if int(status) == -2:  # 删除
            obj = get_object(MailList, request.user, id)
            if obj.is_allow_export:
                obj.isvalid = False
                obj.save()
                messages.add_message(request, messages.SUCCESS, _(u'删除成功'))
            else:
                messages.add_message(request, messages.ERROR, _(u'不能删除  U-Mail租用数据'))
        # if int(status) == -1:  # 清空
        #     address_sqls.deleteAddress(cr, tablename, id)
        #     messages.add_message(request, messages.SUCCESS, _(u'清空地址成功'))
        if int(status) == -9:  # 合并分类
            ids = ids_str.split(',')
            ids = list(MailList.objects.filter(id__in=ids, customer=request.user).values_list('id', flat=True))
            ids_str = ','.join(map(lambda s: str(s), ids))

            ## 合并到新分类
            new_category_name = request.POST.get('new_category_name', "").strip()
            new_category_name = new_category_name or u"新分类"
            is_category = request.POST.get('is_category', "").strip()

            _exists = MailList.objects.filter(id__in=ids, is_allow_export=False).exists()
            if _exists:
                messages.add_message(request, messages.ERROR, _(u'合并分类失败，不能合并  U-Mail租用数据'))
            else:
                if is_category == '2':
                    mergeNewMaillist(request.user.id, ids, ids_str, id_del, new_category_name)
                else:
                    mergeMaillist(request.user.id, id, ids, ids_str, id_del)
                messages.add_message(request, messages.SUCCESS, _(u'合并分类成功'))
        if int(status) == -10:  # 删除分类
            ids = ids_str.split(',')
            _exists = MailList.objects.filter(id__in=ids, is_allow_export=False).exists()
            if _exists:
                messages.add_message(request, messages.ERROR, _(u'不能删除  U-Mail租用数据'))
            else:
                MailList.objects.filter(id__in=ids).update(isvalid=False)
                messages.add_message(request, messages.SUCCESS, _(u'删除分类成功'))
        if int(status) == 20: # 预入库
            obj = get_object(MailList, request.user, id)
            # 行业 ID
            category_id = 29
            ctype = ContentType.objects.get_for_model(obj)
            tag_ids =TaggedItem.objects.filter(content_type=ctype, object_id=int(id)).values_list('tag_id', flat=True)
            # _exists = Tag.objects.filter(category_id=category_id, id__in=tag_ids).exists()
            _exists = Tag.objects.filter(id__in=tag_ids).exists()
            if not _exists:
                # messages.add_message(request, messages.ERROR, u'预入库必须具备一个行业标签')
                messages.add_message(request, messages.ERROR, u'预入库必须具备一个标签')
                return HttpResponseRedirect('/address/?isvalid={}'.format(isvalid))

            admin_id = request.session.get('admin_id', '')
            obj.status = '2'
            obj.manager_id = int(admin_id)
            obj.in_date = time.strftime("%Y-%m-%d %H:%M:%S")
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'预入库成功')
        if int(status) == 21: # 批量预入库
            admin_id = request.session.get('admin_id', '')
            ids = ids_str.split(',')
            objs = MailList.objects.filter(customer=request.user, status='1', id__in=ids, is_allow_export=True)
            other_ids=[]
            if objs:
                # category_id = 29
                ctype = ContentType.objects.get_for_model(objs[0])
                for obj in objs:
                    tag_ids =TaggedItem.objects.filter(content_type=ctype, object_id=obj.id).values_list('tag_id', flat=True)
                    # _exists = Tag.objects.filter(category_id=category_id, id__in=tag_ids).exists()
                    _exists = Tag.objects.filter(id__in=tag_ids).exists()
                    if not _exists:
                        continue
                    other_ids.append(obj.id)

            MailList.objects.filter(customer=request.user, status='1', id__in=other_ids, is_allow_export=True).update(
                status='2', manager_id=int(admin_id), in_date=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            messages.add_message(request, messages.SUCCESS, u'预入库成功')
        if int(status) == -99: # 单个删除共享地址池
            ShareMailList.objects.filter(maillist_id=id, user_id=request.user.id).delete()
            messages.add_message(request, messages.SUCCESS, _(u'删除共享联系人成功'))
        return HttpResponseRedirect('/address/?isvalid={}'.format(isvalid))
    return render(request, 'address/ml_maillist.html', context={'isvalid': isvalid})

# ajax 加载联系人分类
@login_required
def ajax_ml_maillist(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    isvalid = data.get('isvalid', '')
    colums = ['id', 'id', 'subject', 'description', 'id', 'count_real', 'count_subscriber']

    lists = MailList.objects.filter(
        Q(customer=request.user) |  Q(sub_share_maillist__user=request.user))
    if not request.session.get('is_admin', False):
        lists = lists.filter(is_smtp=False)
        lists = lists.filter(is_shield=False)
    if isvalid == '1':
        lists = lists.filter(isvalid=True)
    elif isvalid == '2':
        lists = lists.filter(isvalid=False)
    else:
        lists = lists.filter(id=None)

    if search:
        lists = lists.filter(subject__icontains=search)

    if order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        start_num = int(data.get('start', '0'))
        page = start_num / length + 1
    except ValueError:
        start_num = 0
        page = 1
    count = lists.count()
    if start_num >= count:
        page = 1
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page-1) + 1

    for d in lists.object_list:
        is_not_share = True if d.customer_id == request.user.id else False
        t = TemplateResponse(request, 'address/ajax_ml_maillist.html', {'d': d, 'number': number, 'is_not_share': is_not_share,})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

@login_required
def ajax_export_limit(request, user_id, list_id):
    msg = 'Y'
    if request.user.service().disabled == '1':
        return HttpResponse(json.dumps({'msg': "N"}), content_type="application/json")
    obj = MailList.objects.filter(id=list_id, customer_id=user_id).first()
    if obj and not obj.is_allow_export:
        return HttpResponse(json.dumps({'msg': "N"}), content_type="application/json")
    cr = connections['mm-pool'].cursor()
    try:
        sql = "SELECT COUNT(1) FROM ml_subscriber_{} WHERE list_id={};".format(user_id, list_id)
        cr.execute(sql)
        data = cr.fetchone()
        count = data[0] if data else 0
    except:
        count = 0
    if count > 100000:
        msg = 'N'
    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")

# 获取数量
@login_required
def ajax_maillist_count(request, list_id):
    status = request.GET.get('status', '')
    cr = connections['mm-pool'].cursor()
    user_id = model_addresses.get_address_userid(request, list_id)
    if status == '1':
        count = address_sqls.get_addr_count(cr, user_id, list_id, status)
        html = '<a type="button" href="/address/subscribe/{}/" target="_blank" title="{}">{}</a>'.format(list_id, _(u'查看联系人分类邮箱列表'), count)
        return HttpResponse(json.dumps({'info': html}), content_type="application/json")
    elif status == '2':
        count = address_sqls.get_addr_count(cr, user_id, list_id, status)
        html = '<a type="button" href="/address/subscribe/{}/?is_subscribe=2" target="_blank" title="{}">{}</a>'.format(list_id, _(u'查看订阅用户列表'), count)
        return HttpResponse(json.dumps({'info': html}), content_type="application/json")
    elif status == '3':
        count = address_sqls.get_addr_count(cr, user_id, list_id, status)
        html = '<a type="button" href="/address/unsubscribe/{}/?is_subscribe=2" target="_blank" title="{}">{}</a>'.format(list_id, _(u'查看退订用户列表'), count)
        return HttpResponse(json.dumps({'info': html}), content_type="application/json")
    else:
        raise Http404

# 添加 联系人分类
@login_required
def ml_maillist_add(request):
    form = MailListForm(request.user)
    if request.method == "POST":
        form = MailListForm(request.user, request.POST)
        if form.is_valid():
            obj = form.save()
            return HttpResponseRedirect('/address/maintain/{}/'.format(obj.id))
    return render(request, 'address/ml_maillist_modify.html', context={
        'form': form,
        'ml_maillist_flag': 1,
        'list_id': '',
        'edm_web_url': settings.EDM_WEB_URL,
        'is_allow_export': True,
    })

# 修改 联系人分类
@login_required
def ml_maillist_modify(request, list_id):
    obj = get_object(MailList, request.user, list_id)
    form = MailListForm(request.user, instance=obj)
    if request.method == "POST":
        status = request.POST.get('status', '')
        form = MailListForm(request.user, request.POST, instance=obj)
        if status == 'allow':
            url = '/address/maintain/{}/'.format(list_id)
        elif status == 'notallow':
            url = '/address/?isvalid=1'
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(url)
    return render(request, 'address/ml_maillist_modify.html', context={
        'form': form,
        'ml_maillist_flag': 2,
        'list_id': list_id,
        'edm_web_url': settings.EDM_WEB_URL,
        'is_allow_export': obj.is_allow_export,
    })

# 批量上传地址文件
@csrf_exempt
def ml_addr_multi_upload(request, list_id):
    user_id = request.POST.get('user_id', '')
    # is_disorder = request.POST.get('is_disorder', '')
    # is_disorder = True if is_disorder.lower() == 'true' else False
    is_disorder=True
    is_ignore = request.POST.get('is_ignore', '')
    is_ignore = True if is_ignore.lower() == 'true' else False
    try:
        obj = MailList.objects.get(customer_id=user_id, id=list_id)
    except:
        return HttpResponse(json.dumps({'status': 'M'}), content_type="application/json")

    attachfile = request.FILES.get('filedata', None)
    if not attachfile:
        return HttpResponse(json.dumps({'status': 'N'}), content_type="application/json")

    filename = attachfile.name
    suffix = filename.split('.')[-1]
    if suffix.lower() not in ('xls', 'xlsx', 'csv', 'txt', 'zip', 'rar', 'docx'):
        return HttpResponse(json.dumps({'status': 'S'}), content_type="application/json")

    filepath = os.path.join(
        settings.ADDRESS_IMPORT_PATH,
        '{}_{}.{}'.format(int(time.time()), random.randint(10000, 99999), suffix)
    )
    with open(filepath, 'w') as fw:
        fw.write(attachfile.read())
    cr = connections['mm-pool'].cursor()
    address_sqls.checkTable(cr, request.user.id)
    #　标志列表正在导入
    obj.is_importing = True
    obj.save()
    AddressImportLog.objects.create(
        maillist_id=list_id, customer_id=user_id, filename=filename,
        filepath=filepath, is_disorder=is_disorder, is_newimport=True, is_ignore=is_ignore
    )
    if request.user.service().is_auto_duplicate:
        redis = get_redis_connection()
        redis.rpush(EDM_WEB_MAIL_DUPLICATE_QUEUE, int(user_id))
    return HttpResponse(json.dumps({'status': 'Y'}), content_type="application/json")

# 上传 地址文件
@login_required
def ml_maillist_upload(request):
    if request.method == "POST":
        file = request.FILES[u'files[]']
        is_disorder = request.POST.get('is_disorder', '')
        is_ignore = request.POST.get('is_ignore', '')
        maillist_id = int(request.GET.get('maillist', 0))
        is_disorder = True if is_disorder.lower() == 'true' else False
        is_ignore = True if is_ignore.lower() == 'true' else False

        if not maillist_id or (maillist_id and MailList.objects.filter(id=maillist_id, customer=request.user)):
            filepath = os.path.join(
                settings.ADDRESS_IMPORT_PATH,
                '{}_{}.{}'.format(int(time.time()), random.randint(10000, 99999),
                                  file.name.split('.')[-1])
            )
            with open(filepath, 'w') as fw:
                fw.write(file.read())
            cr = connections['mm-pool'].cursor()
            address_sqls.checkTable(cr, request.user.id)
            AddressImportLog.objects.create(
                maillist_id=maillist_id, customer=request.user, filename=file.name,
                filepath=filepath, is_disorder=is_disorder, is_newimport=True, is_ignore=is_ignore
            )
        return JsonResponse({'result': {}})
    return render(request, 'address/ml_maillist_upload.html', context={})

# 地址导入记录
@login_required
def ml_import_log(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        type = request.POST.get('type')
        filename = '{}_maillist_err_t{}.txt'.format(id, type)
        filepath = os.path.join("/usr/local/mail-import/data/", filename)
        if os.path.exists(filepath):
            wrapper = FileWrapper(file(filepath))
            response = HttpResponse(wrapper, content_type='application/octet-stream')
            response['Content-Length'] = os.path.getsize(filepath)
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response
        else:
            messages.add_message(request, messages.ERROR, _(u'文件不存在'))
            return HttpResponseRedirect(reverse('ml_import_log'))
    return render(request, 'address/ml_import_log.html', context={})

@login_required
def ajax_ml_import_log(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'id', 'filename', 'maillist_id', 'status', 'count_all', 'count_err_1']

    lists = AddressImportLog.objects.filter(customer_id=request.user.id)

    if search:
        lists = lists.filter(filename__icontains=search)

    if order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        start_num = int(data.get('start', '0'))
        page = start_num / length + 1
    except ValueError:
        start_num = 0
        page = 1
    count = lists.count()
    if start_num >= count:
        page = 1
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page-1) + 1

    for d in lists.object_list:
        t = TemplateResponse(request, 'address/ajax_ml_import_log.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

################################
# 查看无效地址
@login_required
def invalid_view(request, log_id):
    return invalidView(request, log_id)

################################
# 联系人分类管理: 添加地址
@login_required
def ml_maillist_maintain_address(request, list_id):
    obj = get_object(MailList, request.user, list_id)
    if not obj.is_allow_export:
        raise Http404
    subject = model_addresses.get_subject(request, list_id)
    return render(request, 'address/ml_maillist_maintain_address.html', context={
        'subject': subject,
        'list_id': list_id,
    })

# 联系人分类管理: 添加地址到联系人分类
@csrf_exempt
@login_required
def ajax_add_address(request, list_id):
    data = request.POST
    post_data = data.get('post_data', '')
    cr = connections['mm-pool'].cursor()
    customer_id = request.user.id
    address_sqls.checkTable(cr, customer_id)
    tablename = 'ml_subscriber_' + str(customer_id)
    values, _addresses = [], []
    success, fail, repeat, valid = 0, 0, 0, 0
    p = re.compile('^(\w|[-+=.])+@\w+([-.]\w+)*\.(\w+)$')
    p_phone = re.compile(
        r'((\+?86)|(\(\+86\)))?(\s)?(13[012356789][0-9]{8}|15[012356789][0-9]{8}|18[02356789][0-9]{8}|14[57][0-9]{8}|1349[0-9]{7}|177[0-9]{8})')
    var_lists = get_addr_var_fields(cr, request.user.id)
    # field_str = u'(list_id, address, fullname, sex, birthday, phone, area, {}, created)'.format(','.join(var_lists))
    mongo = pymongo.MongoClient(host='mongodb://{username}:{password}@{host}:{port}/{dbname}'.format(**mongo_cfg))
    db = mongo['mm-mc'].badmail

    import_obj = AddressImportLog.objects.create(
        maillist_id=list_id, customer=request.user, filename=None,
        filepath=None, status='1', count_all=0,
        count_err_1=0, count_err_2=0,
        time_import=time.strftime("%Y-%m-%d %H:%M:%S"), time_finish=time.strftime("%Y-%m-%d %H:%M:%S")
    )
    # 错误类型 1
    err_t1_name = '{}_maillist_err_t1.txt'.format(import_obj.id)
    err_t1_path = os.path.join("/usr/local/mail-import/data/", err_t1_name)
    fp_err_t1 = open(err_t1_path, "a")

    # 错误类型 2
    err_t2_name = '{}_maillist_err_t2.txt'.format(import_obj.id)
    err_t2_path = os.path.join("/usr/local/mail-import/data/", err_t2_name)
    fp_err_t2 = open(err_t2_path, "a")

    redis = get_redis_connection()
    for d in post_data.split('\n'):
        l = d.strip().replace('\r', '').replace(u'；', ';')
        l = l.split(";")
        length = len(l)
        if ( length == 1 and not l[0].strip() ) or ( not l ):
            continue

        # 判断邮箱地址格式
        if l and not p.match(l[0].strip()):
            fail += 1
            address_tools.save_error_addr(fp_err_t1, l[0])
            continue

        address = l[0].strip()
        if address.split('@')[-1] in (u'yahoo.com.cn', u'yahoo.cn'):
            valid += 1
            address_tools.save_error_addr(fp_err_t1, l[0])
            continue

        if db.find_one({"addr": address}):
            valid += 1
            address_tools.save_error_addr(fp_err_t1, l[0])
            continue

        # 判断重复
        cr.execute(u"SELECT address_id FROM {} WHERE address='{}' AND list_id={} LIMIT 1;".format(tablename, address, list_id))
        if cr.fetchone():
            repeat += 1
            address_tools.save_error_addr(fp_err_t2, l[0])
            continue

        if address in _addresses:
            repeat += 1
            address_tools.save_error_addr(fp_err_t2, l[0])
            continue

        if check_qq_addr(address):
            redis.lpush(GLB_REDIS_REMOTE_GET_QQ, address)

        _addresses.append(address)
        try:
            fullname = l[1].strip() if l[1].strip() else '@'.join(address.split("@")[:-1])
        except:
            fullname = '@'.join(address.split("@")[:-1])

        sex = l[2].strip() if length > 2 else ''
        sex = address_tools.handleSex(sex)

        birthday = l[3].strip() if length > 3 else ''
        birthday = address_tools.hanfBirthday(birthday)

        phone = l[4].strip() if length > 4 else ''
        m = p_phone.search(phone)
        phone = m.group() if m else ''

        area = l[5].strip() if length > 5 else ''
        vars = l[6:]
        sql_parts, sql_args = get_fields_args(var_lists, vars)
        sql  = "INSERT INTO `mm-pool`.`ml_subscriber_%s` SET list_id=%s, address=%s, fullname=%s, sex=%s, birthday=%s, phone=%s, area=%s, created=%s{}".format(sql_parts)
        args = [customer_id, list_id, address, fullname, sex, birthday, phone, area, time.strftime("%Y-%m-%d %H:%M:%S")] + sql_args
        cr.execute(sql, args)
        success += 1
    msg = _(
        u'成功提交%(success)d条记录, 其中有%(repeat)d条重复记录, %(fail)d条格式错误, %(valid)d条无效地址'
    ) % {
              'success': success,
              'repeat': repeat,
              'fail': fail,
              'valid': valid,
          }

    obj = MailList.objects.filter(id=list_id).first()
    if obj:
        obj.count_all = F('count_all') + success + fail + valid
        obj.count_err = F('count_err') + fail + valid
        obj.updated = time.strftime("%Y-%m-%d %H:%M:%S")
        obj.save()

    import_obj.count_all = success + fail + valid + repeat
    import_obj.count_err_1 = fail + valid
    import_obj.count_err_2 = repeat
    import_obj.time_finish = time.strftime("%Y-%m-%d %H:%M:%S")
    import_obj.save()
    if int(success) > 0:
        redis.rpush(EDM_WEB_USER_MAIL_IMPORT_COUNT_QUEUE, '{}_{}'.format(customer_id, list_id))
        if request.user.service().is_auto_duplicate:
            redis.rpush(EDM_WEB_MAIL_DUPLICATE_QUEUE, int(customer_id))

    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")

# #### 订阅地址 #####
@login_required
def ml_subscribe_list(request, list_id):
    obj = model_addresses.get_address_obj(request, list_id)
    user_id = obj.customer_id
    if request.user.id == user_id:
        is_modify_flag = obj.is_allow_export
    else:
        is_modify_flag = False
    # obj = get_object(MailList, request.user, list_id)
    # is_modify_flag = obj.is_allow_export
    subject = model_addresses.get_subject(request, list_id, obj)
    is_subscribe = request.GET.get('is_subscribe', '')
    cr = connections['mm-pool'].cursor()
    address_sqls.checkTable(cr, user_id)
    if request.method == "POST":
        obj2 = get_object(MailList, request.user, list_id)
        tablename = 'ml_subscriber_' + str(request.user.id)
        id = request.POST.get('id', False)
        ids = request.POST.get('ids', '')
        status = int(request.POST.get('status', False))
        redis = get_redis_connection()
        if int(status) == -2:  # 单个删除
            sql = "DELETE FROM {0} WHERE address_id={1}".format(tablename, id)
            cr.execute(sql)
            messages.add_message(request, messages.SUCCESS, _(u'成功删除'))
            redis.rpush(EDM_WEB_USER_MAIL_IMPORT_COUNT_QUEUE, '{}_{}'.format(request.user.id, list_id))
            return HttpResponseRedirect("/address/subscribe/{}/".format(list_id))
        if int(status) == -1:  # 批量删除
            sql = "DELETE FROM {0} WHERE address_id IN ({1})".format(tablename, ids)
            cr.execute(sql)
            messages.add_message(request, messages.SUCCESS, _(u'成功删除'))
            redis.rpush(EDM_WEB_USER_MAIL_IMPORT_COUNT_QUEUE,  '{}_{}'.format(request.user.id, list_id))
            return HttpResponseRedirect("/address/subscribe/{}/".format(list_id))

    var_lists = get_addr_var_fields(cr, request.user.id)
    field_lists = []
    for i in xrange(len(var_lists)-10):
        field_lists.append(u'变量{}'.format(11+i))
    return render(request, 'address/ml_subscribe_list.html', context={
        'subject': subject,
        'list_id': list_id,
        'is_subscribe': is_subscribe,
        'field_lists': field_lists,
        'is_modify_flag': is_modify_flag,
    })


@login_required
def ajax_subscribe_list(request, list_id):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    is_subscribe = data.get('is_subscribe', '')
    colums = ['address_id', 'address_id', 'address', 'is_subscribe', 'activity']

    obj = model_addresses.get_address_obj(request, list_id)
    user_id = obj.customer_id
    if request.user.id == user_id:
        is_modify_flag = obj.is_allow_export
    else:
        is_modify_flag = False
    # obj = get_object(MailList, request.user, list_id)
    # is_modify_flag = obj.is_allow_export

    where_str = u'list_id={}'.format(list_id)
    if is_subscribe == '1':
        where_str += u" and is_subscribe=0 "
    elif is_subscribe == '2':
        where_str += u" and is_subscribe=1 "
    elif is_subscribe == '3':
        where_str += u" and is_subscribe=2 "

    order_by_str = ''
    if order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            order_by_str = u'order by %s desc' % colums[int(order_column)]
        else:
            order_by_str = u'order by %s asc' % colums[int(order_column)]

    if not is_modify_flag:
        if validators.check_email(search):
            where_str += u""" and address='{}' """.format(search)
        elif search:
            where_str += u""" and 1=0 """
    elif is_modify_flag and search:
        where_str += u""" and address like '%{0}%' """.format(search)

    cr = connections['mm-pool'].cursor()
    tablename = 'ml_subscriber_' + str(user_id)
    sql = u"SELECT COUNT(1) FROM %s WHERE %s;" % (tablename, where_str)
    cr.execute(sql)
    rows = cr.fetchall()
    count = rows[0][0]

    var_lists = get_addr_var_fields(cr, user_id)
    field_str = ','.join(var_lists)

    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1
    if not is_modify_flag and length > 25:
        length = 25
    else:
        length = min(length, 500)

    try:
        start_num = int(data.get('start', '0'))
    except ValueError:
        start_num = 0
    if start_num >= count:
        start_num = 0
    page = start_num / length + 1

    if not is_modify_flag and page>5:
        rows = []
    else:
        limit_str = u'limit %s offset %s' % (length, start_num)
        sql = u"""
        SELECT address_id, address, fullname, is_subscribe,
                sex, birthday, phone, activity, area, created, updated,
                %s
        FROM %s WHERE %s %s %s;
        """ % (field_str, tablename, where_str, order_by_str, limit_str)
        cr.execute(sql)
        rows = cr.fetchall()
    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}

    # number = length * (page - 1) + 1
    _lambda_var = lambda s: s if s else ''
    for r in rows:
        address_id, address, fullname, is_subscribe, sex, birthday, phone, activity, area, created, updated = r[:11]
        varList = [_lambda_var(i) for i in list(r[11:])]
        if is_modify_flag:
            operate = u"""
            <a data-toggle="modal" href="/address/subscribe/modify/{0}/{1}/" data-target="#myModal" data-whatever="" class="btn btn-outline btn-primary btn-xs">{2}</a>
            <a type="button" class="btn btn-outline btn-danger btn-xs" href="Javascript: SetStatus({1}, '-2')">{3}</a>
            """.format(list_id, address_id, _(u'修改'), _(u'删除'))
        else:
            operate = ""
        issubscribe = u'是' if is_subscribe else u'否'
        if sex == 'M':
            sex = _(u'男')
        elif sex == 'F':
            sex = _(u"女")
        else:
            sex = ''

        activity_obj = EmailOpenClick.objects.filter(email=address).first()
        activity = activity_obj.activity if activity_obj else 0

        birthday = birthday if birthday != '0000-00-00' else '-'
        activity_s = u'<i class="fa fa-star myself-text-color-ccc"></i>' * 5
        if 0 < activity < 5:
            activity_r = u'<i class="fa fa-star text-primary"></i>' * activity
            activity_v = u'<i class="fa fa-star myself-text-color-ccc"></i>' * (5 - activity)
            activity_s = u"{}{}".format(activity_r, activity_v)
        elif activity >= 5:
            activity_s = u'<i class="fa fa-star text-primary"></i>' * 5
        other = u"""
        <span class="text-nowrap">{6}: <span>{0}</span></span><br>
        <span class="text-nowrap">{7}: <span>{1}</span></span><br>
        <span class="text-nowrap">{8}: <span>{2}</span></span><br>
        <span class="text-nowrap">{9}: <span>{3}</span></span><br>
        <span class="text-nowrap">{10}: <span>{4}</span></span><br>
        <span class="text-nowrap display_none">{11}: <span>{5}</span></span><br>
        """.format(
            fullname, sex, show_click_date(birthday), phone, area, activity_s,
            _(u'姓名'), _(u'性别'), _(u'生日'), _(u'手机'), _(u'地区'), _(u'活跃度')
        )
        aaData = [address_id, address, issubscribe, other] + varList + [
            # u"<span class='text-nowrap'>{}</span><br><span class='text-nowrap'>{}</span>".format(
            #     show_click_datetime(created), show_click_datetime(updated)
            # ),
            operate,
            "",
        ]
        rs["aaData"].append(aaData)
        # number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

# ajax 加载 订阅地址的域名占比
@login_required
def ajax_domain_content(request, list_id):
    is_subscribe = request.GET.get('is_subscribe', '')
    cr = connections['mm-pool'].cursor()
    user_id = model_addresses.get_address_userid(request, list_id)
    tablename = 'ml_subscriber_' + str(user_id)
    vals, count, html = {}, 0, ''
    sql = u"SELECT address FROM {0} WHERE list_id={1}".format(tablename, list_id)
    if is_subscribe == '1':
        sql += u" and is_subscribe=0 "
    elif is_subscribe == '2':
        sql += u" and is_subscribe=1 "
    cr.execute(sql)
    data = cr.fetchall()
    for address in data:
        count += 1
        domain = address[0].split("@")[-1]
        if domain in vals:
            vals[domain] += 1
        else:
            vals.update({domain: 1})
    sortVals = sorted(vals.iteritems(), key=lambda d: d[1], reverse=True)
    i = 0
    for key, value in sortVals:
        occupy = u"{}".format(round(value * 100.00 / count, 2))
        html += u"<span>" + key + u"：<span style='color:green;'>" + occupy + u"%</span></span>&nbsp;&nbsp;"
        i += 1
        if i == 5:
            break
    if not html:
        html = u"<span>{}</span>".format(_(u'无'))
    return HttpResponse(html, content_type='text/html')

# 修改单个订阅地址属性
@login_required
def ml_subscribe_modify(request, list_id, address_id):
    cr = connections['mm-pool'].cursor()
    tablename = 'ml_subscriber_' + str(request.user.id)
    var_lists = get_addr_var_fields(cr, request.user.id)
    if request.method == "POST":
        data = request.POST
        address = data.get('address', '').strip()
        fullname = data.get('fullname', '').strip()
        if not fullname:
            fullname = '@'.join(address.split("@")[:-1])
        phone = data.get('phone', '')
        area = data.get('area', '')
        sex = data.get('sex', '')
        birthday = data.get('birthday', '')
        vars_x =[]
        for var_i in var_lists:
            var_x = data.get(var_i, '')
            vars_x.append(var_x)

        sql_parts, sql_args = get_fields_args(var_lists, vars_x)
        sql = "UPDATE `mm-pool`.`ml_subscriber_%s` SET fullname=%s, sex=%s, birthday=%s, phone=%s, area=%s, created=%s{} WHERE list_id=%s AND address=%s".format(sql_parts)
        args = [request.user.id, fullname, sex, birthday, phone, area, time.strftime("%Y-%m-%d %H:%M:%S")] + sql_args + [list_id, address]
        cr.execute(sql, args)
        messages.add_message(request, messages.SUCCESS, _(u'修改成功'))
        return HttpResponseRedirect("/address/subscribe/{}/".format(list_id))

    field_str = ','.join(var_lists)
    sql = u"""
    SELECT address, fullname, phone, area, sex, birthday, {3}
    FROM {0} WHERE address_id={1} AND list_id={2};
    """.format(tablename, address_id, list_id, field_str)
    cr.execute(sql)
    res = cr.fetchone()
    address, fullname, phone, area, sex, birthday, var1, var2, var3, var4, var5, var6, var7, var8, var9, var10 = res[:16]
    varsList = res[16:]
    forloops = [i+11 for i in xrange(len(varsList))]
    var_vals = zip(forloops, var_lists[:10], varsList)
    return render(request, 'address/ml_subscribe_modify.html', {
        'list_id': list_id,
        'address_id': address_id,
        'address': address,
        'fullname': fullname,
        'phone': phone,
        'area': area,
        'sex': sex,
        'birthday': birthday,
        'var1': var1,
        'var2': var2,
        'var3': var3,
        'var4': var4,
        'var5': var5,
        'var6': var6,
        'var7': var7,
        'var8': var8,
        'var9': var9,
        'var10': var10,
        'var_vals': var_vals,
    })


# #### 退订记录 #####
@login_required
def ml_unsubscribe_list(request, list_id):
    obj = model_addresses.get_address_obj(request, list_id)
    user_id = obj.customer_id
    subject = model_addresses.get_subject(request, list_id, obj)
    cr = connections['mm-pool'].cursor()
    address_sqls.checkTable(cr, user_id)
    if request.method == "POST":
        obj2 = get_object(MailList, request.user, list_id)
        tablename = 'ml_unsubscribe_' + str(request.user.id)
        address = request.POST.get('address', '')
        id = request.POST.get('id', False)
        status = int(request.POST.get('status', False))
        if int(status) == -2:  # 删除
            sql = u"DELETE FROM {0} WHERE list_id={1} AND address='{2}'".format(tablename, id, address)
            cr.execute(sql)
            redis = get_redis_connection()
            redis.rpush(EDM_WEB_USER_MAIL_IMPORT_COUNT_QUEUE,  '{}_{}'.format(request.user.id, list_id))
            messages.add_message(request, messages.SUCCESS, _(u'删除成功'))
        return HttpResponseRedirect("/address/unsubscribe/{}/".format(list_id))
    return render(request, 'address/ml_unsubscribe_list.html', context={
        'subject': subject, 'list_id': list_id
    })


@login_required
def ajax_unsubscribe_list(request, list_id):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['list_id', 'address', 'datetime']

    obj = model_addresses.get_address_obj(request, list_id)
    user_id = obj.customer_id
    if request.user.id == user_id:
        is_modify_flag = obj.is_allow_export
    else:
        is_modify_flag = False

    where_str = u'list_id={}'.format(list_id)
    if search:
        where_str += u""" and address like '%{0}%' """.format(search)

    order_by_str = ''
    if order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            order_by_str = u'order by %s desc' % colums[int(order_column)]
        else:
            order_by_str = u'order by %s asc' % colums[int(order_column)]

    cr = connections['mm-pool'].cursor()
    tablename = 'ml_unsubscribe_' + str(user_id)

    count_sql = u"SELECT COUNT(1) FROM %s WHERE %s;" % (tablename, where_str)
    cr.execute(count_sql)
    rows = cr.fetchall()
    count = rows[0][0]

    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        start_num = int(data.get('start', '0'))
    except ValueError:
        start_num = 0
    if start_num >= count:
        start_num = 0
    limit_str = u'limit %s offset %s' % (length, start_num)
    sql = u"SELECT address, datetime, list_id FROM %s WHERE %s %s %s" % (tablename, where_str, order_by_str, limit_str)
    cr.execute(sql)
    rows = cr.fetchall()
    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    page = start_num / length + 1
    number = length * (page - 1) + 1
    for r in rows:
        if is_modify_flag:
            modify_str = u'''<a type="button" class="btn btn-outline btn-danger btn-xs" href="Javascript: SetStatus({}, '{}', '-2')">{}</a>'''.format(
                r[2], r[0], _(u'删除'))
        else:
            modify_str = ""
        rs["aaData"].append([
            number, r[0], dateformat(r[1], 'Y-m-d H:i:s'),
            modify_str,
            "",
        ])
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


# #### 增加订阅记录 #####
@xframe_options_exempt
def add_subscribe_rec(request):
    try:
        id = request.GET.get('id', '')
        user_id, list_id = id.split(",")
        language = request.GET.get('language', '')
        template_name = 'address/add_subscribe_rec_en.html' if language == 'en' else 'address/add_subscribe_rec.html'
        return render(request, template_name, context={'user_id': user_id, 'list_id': list_id})
    except:
        return HttpResponse(u"<body><p>{}</p></body>".format(_(u'提示信息：参数错误！')))

@csrf_exempt
def ajax_add_subscriber(request):
    if request.method == 'GET':
        raise Http404
    data = request.POST
    user_id = data.get('user_id', '').strip()
    list_id = data.get('list_id', '').strip()
    address = data.get('address', '').strip()
    if not user_id or not address:
        raise Http404
    # fullname = data.get('fullname', '').strip()
    fields = ['list_id', 'address', 'fullname', 'sex', 'birthday', 'phone', 'area', 'var1', 'var2', 'var3', 'var4', 'var5', 'var6', 'var7', 'var8', 'var9', 'var10']
    kwargs = {}
    for f in fields:
        v = data.get(f, '').strip()
        if f == 'sex':
            v = address_tools.handleSex(v)
        elif f == 'birthday':
            v = address_tools.hanfBirthday(v)
        kwargs[f] = v

    cr = connections['mm-pool'].cursor()
    tablename = 'ml_subscriber_' + str(user_id)
    list_id = list_id if MailList.objects.filter(id=list_id).exists() else 0
    if address_sqls.select_address(cr, tablename, address, list_id):
        msg = address_sqls.update_address(cr, tablename, address, list_id)
    else:
        msg = address_sqls.insert_address(cr, tablename, **kwargs)
        redis = get_redis_connection()
        redis.rpush(EDM_WEB_USER_MAIL_IMPORT_COUNT_QUEUE,  '{}_{}'.format(user_id, list_id))
    response = HttpResponse(msg, content_type="text/plain")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

# 导出模板格式文件
@login_required
def export_template_format(request):
    data = request.GET
    file_ext = data.get('file_ext', '').strip()
    cr = connections['mm-pool'].cursor()
    var_lists = get_addr_var_fields(cr, request.user.id)
    forloops = [i+1 for i in xrange(len(var_lists))]
    if request.user.lang_code == 'en-us':
        list = [ [u'Address', u'Name', u'Gender', u'birthday', u'phone', u'area'] + var_lists ]
    else:
        list = [ [u'邮件地址', u'姓名', u'性别', u'生日', u'手机', u'地区'] + [u'变量{}'.format(i) for i in forloops] ]
    if file_ext == 'csv':
        force_csv = True
        mimetype = 'text/csv'
        response = FormatExcelResponse(
            data=list, output_name='address', force_csv=force_csv,
            encoding='gbk', mimetype=mimetype, file_ext=file_ext
        )
    elif file_ext == 'txt':
        force_csv = False
        mimetype = 'text/plain'
        response = FormatExcelResponse(
            data=list, output_name='address', force_csv=force_csv,
            encoding='gbk', mimetype=mimetype, file_ext=file_ext
        )
    elif file_ext == 'xls':
        force_csv = False
        mimetype = 'application/vnd.ms-excel'
        response = FormatExcelResponse(
            data=list, output_name='address', force_csv=force_csv,
            encoding='gbk', mimetype=mimetype, file_ext=file_ext
        )
    elif file_ext == 'xlsx':
        force_csv = False
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = FormatExcelResponse(
            data=list, output_name='address', force_csv=force_csv,
            encoding='gbk', mimetype=mimetype, file_ext=file_ext
        )
    return response

# 导出地址文件
@login_required
def export_address(request, list_id):
    data = request.GET
    cr = connections['mm-pool'].cursor()
    tablename = 'ml_subscriber_' + str(request.user.id)
    file_name = data.get('file_name', '').strip()
    var_lists = get_addr_var_fields(cr, request.user.id)
    forloops = [i+1 for i in xrange(len(var_lists))]
    if request.user.lang_code == 'en-us':
        alist = [ [u'email', u'name', u'gender', u'birthday', u'phone', u'area'] + var_lists ]
    else:
        alist = [ [u'邮件地址', u'姓名', u'性别', u'生日', u'手机', u'地区'] + [u'变量{}'.format(i) for i in forloops] ]
    sql = u"""
    SELECT address, fullname, sex, birthday, phone, area, {2}
    FROM {0} WHERE list_id={1};
    """.format(tablename, list_id, ','.join(var_lists))
    cr.execute(sql)
    for row in cr.fetchall():
        address, fullname, sex, birthday, phone, area = row[:6]
        aaData = list(row[6:])
        if sex == 'M':
            sex = u'男'
        elif sex == 'F':
            sex = u'女'
        else:
            sex = ''
        alist.append([address, fullname, sex, birthday, phone, area] + aaData)
    return ExcelResponse(alist, file_name, encoding='gbk')
