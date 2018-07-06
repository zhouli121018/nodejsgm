#coding=utf-8
import re
import os
import sys
import traceback
import json
import base64
import urlparse
import urllib2
import shutil
import time
import random
import urllib
import datetime
import requests

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django import template
from django.template import Context
from django.db import connections
from django.db.models import Q
from django_redis import get_redis_connection
from django.utils.translation import ugettext_lazy as _
from app.template.configs import ( EDIT_TYPE, ENCODING_TYPE, CHARACTER_TYPE, IMAGE_TYPE, ATTACH_TYPE, PRIORITY_TYPE,
                                   ATTACH_SAVE_PATH, TEMP_SAVE_PATH, EDM_WEB_URL, UPLOAD_JSON_SUFFIX, MB, KB, UPLOAD_ALLOWED_SUFFIX )
from app.template.models import SendTemplate, SendAttachment, SendSubject, RefTemplateCategory, RefTemplate, TestSendTemplateLog, ShareTemplte
from app.address.models import MailList, ComplaintList
from app.task.models import SendContent
from app.template.templatetags.template_tags import filesizeformat
from app.core.models import Prefs, CommonType, SysPicDomain, TestChannel
from app.mosaico.models import Template
from app.mosaico.tools import get_mosaico_key
from app.template.tools import show_mail_replace
from app.address.utils.vars import get_addr_var_fields
from lib.parse_email import ParseEmail
from lib.parse_html2text import delhtml2text
from lib.template import ( decode_str, del_jscss_from_html, replace_srchref_from_html, clear_relative_url, get_html_content,
                           del_filepath, handle_uploaded_attachfile, handle_uploaded_file, handle_get_file,
                           handle_html_attach, handle_get_zipfile, handle_html_zip_attach, send_template, MulTemplateEmail,
                           get_render_attach_template, get_render_refimg_template, decode_encode_str, smtp_send_email, create_filepath,
                           handle_get_rarfile )
from lib.common import get_object, get_smtp_acct
from lib.tools import get_timestamp, file_size_conversion, get_timestamp_last3days
from app.template.utils.share import get_share_template_object, get_share_mosaico_obj

##########  邮件模板管理 ##########
# 模板列表视图
@login_required
def template_list(request):
    isvalid = request.GET.get('isvalid', '')
    if request.method == "POST":
        id = request.POST.get('id', False)
        ids = (request.POST.get('ids', False)).split(',')
        status = int(request.POST.get('status', False))
        if int(status) == -3: # 恢复启用
            obj = SendTemplate.objects.get(id=id, user=request.user)
            obj.isvalid = True
            obj.save()
            msg = _(u'恢复模板（%(name)s）成功') % {'name': obj.name}
        if int(status) == -2: # 单个删除
            SendTemplate.objects.filter(user=request.user, id=id).update(isvalid=False)
            redis = get_redis_connection()
            redis.rpush(settings.EDMWEB_NULL_TEMPLATE_QUEQUE, '{}_{}'.format(request.user.id, id))
            msg = _(u'成功移到回收站')
        if int(status) == -9: # 单个删除共享模板
            ShareTemplte.objects.filter(template_id=id, user_id=request.user.id).delete()
            msg = _(u'删除共享模板成功')
        if int(status) == -1: # 批量删除
            SendTemplate.objects.filter(user=request.user, id__in=ids).update(isvalid=False)
            redis = get_redis_connection()
            redis.rpush(settings.EDMWEB_NULL_TEMPLATE_QUEQUE, '{}_{}'.format(request.user.id, ','.join(ids)))
            msg = _(u'成功移到回收站')
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect('/template/?isvalid={}'.format(isvalid))
    return render(request, template_name='template/template_list.html', context={
        "isvalid": isvalid
    })

# 动态刷新检测结果
@csrf_exempt
@login_required
def ajax_check_result_report(request):
    try:
        template_id = int(request.GET.get('template_id', '0'))
        obj = get_object(SendTemplate, request.user, template_id)
        code, msg, test_html = obj.show_result_img()
        return HttpResponse(json.dumps({'status': 'Y', 'msg': msg, 'code': code, 'test_html': test_html}), content_type="application/json")
    except:
        return HttpResponse(json.dumps({'status': 'N'}), content_type="application/json")

# 检测结果
@login_required
def show_template_report(request):
    template_id = request.GET.get('template_id', '')
    obj = get_object(SendTemplate, request.user, template_id)
    return render(request, 'template/show_template_report.html', {
        'obj': obj,
    })

# ajax 加载模板列表
@login_required
def ajax_template_list(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    isvalid = data.get('isvalid', '')
    colums = ['id', 'id', 'name', 'size', 'created', 'updated', 'result']
    # lists = SendTemplate.objects.filter(user=request.user)
    lists = SendTemplate.objects.filter( Q(user=request.user) | Q(sub_share_template__user=request.user))
    if not request.session.get('is_admin', False):
        lists = lists.filter(is_shield=False)
    if isvalid == '1':
        lists = lists.filter(isvalid=True)
    elif isvalid == '2':
        lists = lists.filter(isvalid=False)
    else:
        lists = lists.filter(isvalid=False).filter(isvalid=True)
    if search:
        lists = lists.filter(name__icontains=search)
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
        is_not_share = True if d.user_id == request.user.id else False
        t = TemplateResponse(request, 'template/ajax_template_list.html', {'d': d, 'number': number, 'is_not_share': is_not_share})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

# 模板列表视图 发送测试
# @ensure_csrf_cookie
@csrf_exempt
@login_required
def ajax_send_template(request):
    data = request.POST
    template_id = int(data.get('template_id', ''))
    emails = data.get('emails', '')
    mail_list = emails.split('\n')
    mail_list = [i.strip() for i in mail_list if i.strip() != '']
    timeStamp, timestamp1, timestamp2 = get_timestamp()
    msg = ''
    count = 0
    p = re.compile('^(\w|[-+=.])+@\w+([-.]\w+)*\.(\w+)$')
    for mail in mail_list:
        if not p.match(mail):
            msg = _(u'邮箱格式错误: %(mail)s') % {'mail': mail}
            break
        if count >= 2:
            msg = _(u'邮箱数量不得超过2个') % {}
            break
        count += 1
    if msg:
        return HttpResponse(json.dumps({'msg': msg, 'status': 'N'}), content_type="application/json")
    if not count:
        return HttpResponse(json.dumps({'msg': _(u"请填写邮箱") % {}, 'status': 'N'}), content_type="application/json")

    sucess = 0
    status = 'N'
    msg = _(u"发送失败，请重试") % {}
    # obj = SendTemplate.objects.get(id=template_id, user=request.user)
    obj = get_share_template_object(SendTemplate, request.user, template_id)
    detail = {}
    if request.user.disabled == '1' or request.user.service().disabled == '1':
        return HttpResponse(json.dumps({'msg': _(u'没有权限发送测试') % {}, 'status': 'N'}), content_type="application/json")
    testCount = TestSendTemplateLog.objects.filter(user=request.user, test_time__gte=timestamp1, test_time__lte=timestamp2, status__in=[1,2], user_type='users').count()
    if testCount >= 10:
        return HttpResponse(json.dumps({'msg': _(u'一天最多能进行10次发送测试') % {}, 'status': 'N'}), content_type="application/json")
    testCount = TestSendTemplateLog.objects.filter(user=request.user, template_id=template_id, test_time__gte=timestamp1, test_time__lte=timestamp2, status__in=[1,2], user_type='users').count()
    if testCount >= 6:
        return HttpResponse(json.dumps({'msg': _(u'一个模板一天只能发送6次测试') % {}, 'status': 'N'}), content_type="application/json")
    template_log_obj = TestSendTemplateLog.objects.create(
        user=request.user, template_id=template_id, test_time=timeStamp,
        emails=','.join(mail_list), user_type='users',
        status=2, ext='{}'
    )
    for receiver in mail_list:
        host, port, account, password = get_smtp_acct(receiver)
        message = obj.organize_msg(mail_from=account, mail_to=receiver)
        code, msg_str = smtp_send_email(
            host=host,
            port=port,
            account=account,
            password=password,
            sender=account,
            receivers=[receiver],
            message=message
        )
        detail[receiver] = msg_str
        if code == 250:
            sucess += 1
        channel_obj, _created = TestChannel.objects.get_or_create(email=receiver)
        channel_obj.customer = request.user
        channel_obj.is_quick_send = True
        channel_obj.save()
    if sucess:
        msg, status = _(u"发送成功") % {}, "Y"
        template_log_obj.status=1
        template_log_obj.ext='{"status": "Y"}'
        template_log_obj.save()
    else:
        template_log_obj.status=0
        template_log_obj.ext='{"status": "N", "msg": %s}' % detail
        template_log_obj.save()

    return HttpResponse(json.dumps({'msg': msg, 'status': status}), content_type="application/json")

# 最近3天测试记录
@login_required
def test_template_history(request, template_id):
    timeStamp, timestamp1, timestamp2 = get_timestamp_last3days()
    lists = TestSendTemplateLog.objects.filter(
        user=request.user, template_id=template_id, test_time__gte=timestamp1, test_time__lte=timestamp2
    ).order_by('-id')
    return render(request, 'template/test_template_history.html', {
        'lists': lists,
    })

# 增加模板ID
# @ensure_csrf_cookie
@csrf_exempt
@login_required
def ajax_template_id(request):
    obj = SendTemplate.objects.create(
        user=request.user, content_type=1, encoding='base64', character='utf-8',
        image_encode='N', attachtype='html', priority='low', status='0', isvalid=1, issync=0
    )
    return HttpResponse(json.dumps({'template_id': obj.id}), content_type="application/json")

@login_required
def ajax_copy_template_id(request):
    if request.method == "POST":
        template_id = request.POST.get('template_copy_id', '')
        if template_id:
            tplobj = get_share_template_object(SendTemplate, request.user, template_id)
            obj = SendTemplate.objects.create(
                user=request.user, content_type=1, name=u'{} (copy)'.format(tplobj.name), subject=u'{} (copy)'.format(tplobj.subject),
                content=tplobj.content, text_content=tplobj.text_content,
                encoding=tplobj.encoding, character=tplobj.character,
                image_encode=tplobj.image_encode, attachtype=tplobj.attachtype, priority=tplobj.priority,
                # report=None, result=None, spam_note=None, edm_check_result=None
                size = tplobj.size,
                isvalid=1, issync=1,
                is_mosaico=tplobj.is_mosaico,
            )
            atts = []
            lists = SendAttachment.objects.filter(template_id=template_id, user=request.user)
            copy_id = obj.id
            for d in lists:
                filepath = d.filepath
                src_filepath = os.path.join(ATTACH_SAVE_PATH, str(template_id), filepath)
                atts.append(SendAttachment(template_id=copy_id, user=request.user, filename=d.filename, filetype=d.filetype, filepath=filepath, attachtype=d.attachtype, size=d.size))
                tpl_path = os.path.join(ATTACH_SAVE_PATH, str(copy_id))
                create_filepath(tpl_path)
                file_path = os.path.join(tpl_path, filepath)
                shutil.copyfile(src_filepath, file_path)
            if atts:
                SendAttachment.objects.bulk_create(atts)

            subjects = []
            lists = SendSubject.objects.filter(template_id=template_id)
            for d in lists:
                subjects.append(SendSubject(template_id=copy_id, subject=d.subject))
            if subjects:
                SendSubject.objects.bulk_create(subjects)

            if tplobj.is_mosaico:
                mosaico_obj = get_share_mosaico_obj(Template, request.user, tplobj.id)
                mosaico_key = get_mosaico_key(copy_id)
                mosaico_tplobj, _created = Template.objects.get_or_create(
                    # key=mosaico_key,
                    name=mosaico_obj.name,
                    user_id=request.user.id,
                    template_id=copy_id,
                )
                mosaico_meta_data = mosaico_obj.meta_data
                mosaico_meta_data['created'] = int(time.time())
                mosaico_meta_data['key'] = mosaico_key
                mosaico_tplobj.html = mosaico_obj.html
                mosaico_tplobj.template_data = mosaico_obj.template_data
                mosaico_tplobj.meta_data = mosaico_meta_data
                mosaico_tplobj.save()

            redis = get_redis_connection()
            redis.rpush('template_check', copy_id)
            redis.lpush('edm_web_mail_template_point_queue', json.dumps({
                "user_id": request.user.id,
                'template_id': copy_id,
            }))
            if tplobj.is_mosaico:
                return HttpResponseRedirect(reverse("mosaico_template_modify", args=(copy_id,)))
            else:
                return HttpResponseRedirect(reverse("ck_template", args=(copy_id,)))
                # return HttpResponseRedirect(reverse("template_modify", args=(copy_id,)))
    return Http404

# 提交时校验模板大小
@csrf_exempt
@login_required
def ajax_check_template_size(request):
    data = request.POST
    template_id = int(data.get('template_id', ''))
    c_size = int(data.get('c_size', '0'))
    obj = SendTemplate.objects.get(id=template_id, user=request.user)
    size = obj.get_template_size(c_size)
    size = round(size / (KB * 1.000), 0)
    return HttpResponse(json.dumps({'size': size}), content_type="application/json")

# 更改是否内嵌照片设置，用于KindEditor处理保存数据
@csrf_exempt
@login_required
def ajax_onchange_image_encode(request):
    data = request.POST
    template_id = int(data.get('template_id', ''))
    value = data.get('value', '')
    field = data.get('field', '')
    obj = SendTemplate.objects.get(id=template_id, user=request.user)
    if field == 'image_encode':
        obj.image_encode = value
        obj.save()
    elif field == 'attachtype':
        obj.attachtype = value
        obj.save()
    return HttpResponse(json.dumps({'status': 'Y'}), content_type="application/json")

def _get_pic_url():
    lists = SysPicDomain.objects.filter(isvalid=True)
    domain = None
    if lists:
        obj = random.choice(lists)
        domain = obj.domain
    return domain if domain else random.choice(settings.TEMPLATE_PIC_URLS)

# 模板修改
@login_required
def template_modify(request,template_id):
    obj = get_object(SendTemplate, request.user, template_id)
    if request.method == "POST":
        data = request.POST
        content_type = 1
        name = data.get('name', '')
        create_or_update = data.get('create_or_update', '')
        content = data.get('content', '')
        text_content = u'''如果邮件内容无法正常显示请以超文本格式显示HTML邮件！\n
        （If the content of the message does not display properly, please display the HTML message in hypertext format!）'''
        encoding = data.get('encoding', 'base64')
        character = data.get('character', 'utf-8')
        image_encode = data.get('image_encode', 'N')
        attachtype = data.get('attachtype', 'html')
        size = 0
        if content:
            size += len(content)
        if text_content:
            size += len(text_content)

        subject_list = data.getlist('subject_list[]', '')
        SendSubject.objects.filter(template_id=template_id).delete()
        subject_obj_list, template_subject = [], ''
        for subject in subject_list:
            if subject:
                template_subject = subject
                subject_obj_list.append(SendSubject(template_id=template_id, subject=subject))
        SendSubject.objects.bulk_create(subject_obj_list)

        obj.content_type = content_type
        obj.name = name
        obj.subject = template_subject
        obj.content = content
        obj.text_content = text_content
        obj.encoding = encoding
        obj.character = character
        obj.image_encode = image_encode
        obj.attachtype = attachtype
        obj.size = size
        obj.issync = True
        obj.result = None
        obj.save()
        redis = get_redis_connection()
        redis.rpush('template_check', obj.id)
        redis.lpush('edm_web_mail_template_point_queue', json.dumps({
            "user_id": request.user.id,
            'template_id': template_id,
        }))
        status = _(u'模板添加成功') if create_or_update == '1' else _(u'模板修改成功')
        messages.add_message(request, messages.SUCCESS, status)
        return HttpResponseRedirect('/template/?isvalid=1')

    content_type = obj.content_type
    content = obj.content
    content_type_flag = 0
    if content and content_type == 1:
        content_type_flag = 1
    if SendAttachment.objects.filter(template_id=template_id).exists():
        content_type_flag = 1
    if content_type == 2:
        content_type_flag = 2
    subject_objs = SendSubject.objects.filter(template_id=template_id)

    name_list = ['notview_unsub_complaint_zh', 'notview_unsub_complaint_tw', 'notview_unsub_complaint_en',
                 'notview_unsub_complaint_ko', 'notview_unsub_complaint_ja', 'notview_unsub_complaint_ru']
    service_list = Prefs.objects.filter(name__in=name_list).values_list('name', 'value')
    service_vlas = dict(service_list)
    for key in name_list:
        if key not in service_vlas.keys():
            service_vlas.update({key: ''})

    django_html = obj.render_attach_template()
    cate_objs = RefTemplateCategory.objects.all()

    common_var_link, common_var_content = {}, {}
    common_var_lists = CommonType.objects.filter(disabled=True)
    redis = get_redis_connection()
    # common_var_lists = []
    for d in common_var_lists:
        count = redis.hget(settings.COMMON_VAR_COUNT_HASH, key=d.var_type)
        count = int(count) if count else 0
        if request.user.lang_code == 'en-us':
            common_var_link.update({ d.var_type.upper(): u'{} ({})'.format(d.var_type, count) })
        else:
            common_var_link.update({ d.var_type.upper(): u'{} ({}条)'.format(d.name, count) })
        common_var_content.update({ d.var_type.upper(): d.dict_type })

    cr = connections['mm-pool'].cursor()
    var_lists = get_addr_var_fields(cr, request.user.id)
    if request.user.lang_code == 'en-us':
        customer_var_link = [
            {'RECIPIENTS'	: u'Recipient Aaddress'},
            {'FULLNAME'	: u'Recipient'},
            {'DATE'	: u'Current date'},
            {'RANDOM_NUMBER'	: u'Random 10 digits'},
            {'RANDOM_HTML'	: u'Random 200 Chinese characters'},
            {'SEX':     u'Gender'},
            {'BIRTHDAY':     u'Birthday'},
            {'PHONE':     u'Phone'},
            {'AREA':     u'Area'},
        ]
        subject_vals = [
            ('{FULLNAME}', u'Recipient Name'),
            ('{RECIPIENTS}',  u'Recipient'),
            ('{DATE}',  u'Current date'),
            ('{RANDOM_NUMBER}',  u'Random 10 digits'),
            ('{SEX}', u'Gender'),
            ('{BIRTHDAY}', u'Birthday'),
            ('{PHONE}', u'Phone'),
            ('{AREA}',    u'Area'),
        ]
    else:
        customer_var_link = [
            {'RECIPIENTS'	: u'收件人地址'},
            {'FULLNAME'	: u'收件人姓名'},
            {'DATE'	: u'当前日期'},
            {'RANDOM_NUMBER'	: u'随机10位数'},
            {'RANDOM_HTML'	: u'随机200中文字符（自动隐藏,Gmail无效）'},
            {'SEX':     u'性别'},
            {'BIRTHDAY':     u'生日'},
            {'PHONE':     u'手机'},
            {'AREA':     u'地区'},
        ]
        subject_vals = [
            ('{FULLNAME}', u'收件人姓名'),
            ('{RECIPIENTS}',  u'收件人地址'),
            ('{DATE}',  u'当前日期'),
            ('{RANDOM_NUMBER}',  u'随机10位数字'),
            ('{SEX}', u'性别'),
            ('{BIRTHDAY}', u'生日'),
            ('{PHONE}', u'手机'),
            ('{AREA}', u'地区'),
        ]
    customer_var_content = {
        'RECIPIENTS'		: '{RECIPIENTS}',
        'FULLNAME'	: '{FULLNAME}',
        'DATE'	: '{DATE}',
        'RANDOM_NUMBER'	: '{RANDOM_NUMBER}',
        'RANDOM_HTML'	: '{RANDOM_HTML}',
        'SEX':     '{SEX}',
        'BIRTHDAY':     '{BIRTHDAY}',
        'PHONE':     '{PHONE}',
        'AREA':     '{AREA}',
    }
    for index, var_x in enumerate(var_lists, start=1):
        if request.user.lang_code == 'en-us':
            customer_var_link.append({var_x.upper(): u'var{}'.format(index) })
            subject_vals.append(('{' + var_x.upper() +'}', u'var{}'.format(index)))
        else:
            customer_var_link.append({var_x.upper(): u'变量{}'.format(index) })
            subject_vals.append(('{' + var_x.upper() +'}', u'变量{}'.format(index)))
        customer_var_content.update({ var_x.upper(): '{'+ var_x.upper() +'}'})

    context = {
        'template_obj': obj,
        'content_type_flag': content_type_flag,
        'subject_objs': subject_objs,
        'subject_vars': subject_vals,
        'cate_objs': cate_objs,
        'template_id': template_id,

        'edit_types': EDIT_TYPE,
        'encoding_types': ENCODING_TYPE,
        'character_types': CHARACTER_TYPE,
        'image_encode_types': IMAGE_TYPE,
        'attachtype_types': ATTACH_TYPE,
        'priority_types': PRIORITY_TYPE,

        'attach_list': django_html,
        'service': json.dumps(service_vlas),
        'uploadJson_url':  json.dumps(EDM_WEB_URL + '/template/ajax_upload_json/'),
        'jsonUrl': json.dumps(_get_pic_url()),

        'common_var_link': json.dumps(common_var_link),
        'common_var_content': json.dumps(common_var_content),

        'customer_var_link': json.dumps(customer_var_link),
        'customer_var_content': json.dumps(customer_var_content),
    }
    return render(request, template_name='template/template_modify.html', context=context)

@login_required
def ajax_save_template(request, template_id):
    obj = get_object(SendTemplate, request.user, template_id)
    msg = _(u"保存出错")
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            obj.content = content
            obj.save()
        msg = _(u'%(time)s保存成功') % {"time": datetime.datetime.now().strftime("%H:%M:%S") }
    return HttpResponse(msg, content_type="text/plain")


# 预览或下载eml
@login_required
def template_preview(request, template_id):
    obj = get_share_template_object(SendTemplate, request.user, template_id)
    if obj.content_type == 1:
        charset = obj.character if obj.character else 'utf-8'
        return HttpResponse(obj.content, charset=charset)
    elif obj.content_type == 2:
        response = HttpResponse(obj.content.replace("\r\n", "\n"), content_type='text/html')
        response['Content-Disposition'] = 'attachment; filename="eml.eml"'
        return response

# url 提交
@csrf_exempt
@login_required
def ajax_get_content_from_url(request, template_id):
    try:
        obj = get_object(SendTemplate, request.user, template_id)
        obj.delete_attach(attachtype='html')
        data = request.POST
        html_url = data.get('html_url', '')
        parse = urlparse.urlparse(html_url)
        if parse.scheme == 'http' and (parse.port is None or parse.port==80):
            pass
        elif parse.scheme == 'https' and  (parse.port is None or parse.port==443):
            pass
        else:
            return HttpResponse(json.dumps({'status': 'N', 'msg': _(u'平台只允许HTTP80 HTTPS443端口网页模板的抓取！') % {} }), content_type="application/json")

        # src = "/static/aa.png" 用 url2 拼接
        # src = "static/aa.png" 用 url 拼接
        urltype, url = urllib2.splittype(html_url)
        if not urltype:
            return HttpResponse(json.dumps({'status': 'N', 'msg': _(u'平台只允许HTTP80 HTTPS443端口网页模板的抓取！') % {} }), content_type="application/json")
        else:
            host, selector = urllib2.splithost(url)
            url2 = urltype + '://' + host
        url = '/'.join(html_url.split('/')[:-1])
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        try:
            # r = requests.get(url, headers=headers)
            # content = r.content
            req = urllib2.Request(url=html_url, headers=headers)
            content = urllib2.urlopen(req).read()
        except:
            # r = requests.get(url, headers=headers, timeout=10)
            # content = r.content
            content = urllib2.urlopen(html_url, timeout=10).read()
        content = decode_str(content)
        content = del_jscss_from_html(content)
        content = replace_srchref_from_html(url, url2, content)
        return HttpResponse(json.dumps({'status': 'Y', 'msg': _(u'提交成功') % {}, 'content': content}), content_type="application/json")
    except urllib2.HTTPError as e:
        print e.code
        return HttpResponse(json.dumps({'status': 'N', 'msg': _(u'访问url失败,请重试') % {} }), content_type="application/json")
    except urllib2.URLError as e:
        print e
        return HttpResponse(json.dumps({'status': 'N', 'msg': _(u'访问url出错,请重试') % {} }), content_type="application/json")
    except BaseException as e:
        print e
        return HttpResponse(json.dumps({'status': 'N', 'msg': _(u'提交异常,请重试') % {} }), content_type="application/json")

# html、eml、zip 提交
@csrf_exempt
@login_required
def ajax_get_html_content(request):
    data = request.POST
    if not data:
        data = request.GET
    template_id = int(data.get('template_id', ''))
    edit_type = data.get('edit_type', '')
    type_name = data.get('type_name', '')
    tpl_attachtype = data.get('attachtype', '')
    if not tpl_attachtype:
        tpl_attachtype = 'common'
    file = request.FILES.get(type_name, None)
    if file.size > 2 * KB * KB:
        msg = {'status': 'N', 'msg': _(u'文件大小不能大于2M') % {}, 'content': ''}
        return HttpResponse(json.dumps(msg), content_type="application/json")
    obj = SendTemplate.objects.get(id=template_id, user=request.user)
    obj.delete_attach(attachtype='html')
    if edit_type == '3':
        # html上传
        content = file.read()
        content = del_jscss_from_html(content)
        content = clear_relative_url(content)
        content = decode_str(content)
        django_html = obj.render_attach_template()
        msg = {'status': 'Y', 'msg': _(u'提交成功')%{}, 'content': content, 'attach': django_html, 'edit_type': '3'}
        return HttpResponse(json.dumps(msg), content_type="text/plain")
        # return HttpResponse(json.dumps(msg), content_type="application/json")
    elif edit_type == '4':
        # eml文件导入
        path = TEMP_SAVE_PATH
        handle_uploaded_file(template_id, file, path)
        content = handle_get_file(template_id, path)
        content = content.replace("\r\n", "\n")
        p = ParseEmail(content)
        data = p.parseMailTemplate()
        content = data.get('html_text', '')
        html_charset = data.get('html_charset', '')
        text_content = data.get('plain_text', '')
        plain_charset = data.get('plain_charset', '')
        if content:
            content = decode_str(content, html_charset)
        if text_content:
            text_content = decode_str(text_content, plain_charset)
        for att in data['attachments']:
            file_name, ufile_name, file_type, attachtype, attachsize = handle_html_attach(template_id, att, tpl_attachtype)
            att_obj = SendAttachment(
                user_id=request.user.id, template_id=template_id,
                filename=file_name, filetype=file_type, filepath=ufile_name, attachtype=attachtype, size=attachsize
            )
            att_obj.save()
            if 'content_id' in att:
                # 模板类型html:以eml格式上传，网络附件以唯一标识名作为查询( cid=ufile_name)
                pattern = u'"cid:{}"'.format(att['content_id'])
                link = u'{}?id={}&ufile_name={}&aid=1'.format(
                    _get_pic_url() + '/template/ajax_get_network_attach/', template_id, ufile_name)
                content = re.sub(pattern, link, content)
            if attachtype == 'html' and 'content_id' not in att:
                ajax_url = _get_pic_url() + '/template/ajax_get_network_attach/'
                file_size = filesizeformat(att['size'])
                content = get_html_content(content, ajax_url, template_id, ufile_name, file_type, file_name, file_size)
        django_html = obj.render_attach_template()
        msg = {'status': 'Y', 'msg': _(u'提交成功')%{}, 'content': content, 'text_content_c': text_content, 'attach': django_html, 'edit_type': '4'}
        return HttpResponse(json.dumps(msg), content_type="text/plain")
        # return HttpResponse(json.dumps(msg), content_type="application/json")
    elif edit_type == '5':
        # zip导入
        path = TEMP_SAVE_PATH
        save_path = os.path.join(path, "{}".format(str(template_id)))
        try:
            del_filepath(save_path)
        except:
            pass
        fext = os.path.splitext(file.name)[-1][1:]
        handle_uploaded_file(template_id, file, path, suffix=fext)
        if fext == 'rar':
            html_file, att_files, save_path = handle_get_rarfile(template_id, path)
        elif fext == 'zip':
            html_file, att_files, save_path = handle_get_zipfile(template_id, path)
        if html_file:
            html_file = os.path.join(save_path, html_file)
            with open(html_file, 'r') as f:
                content = f.read()
                content = decode_str(content)
            pattern = ur'src="(.*?)"'
            pattern2 = ur'url\(\'(.*?)\'\)'
            pattern4 = ur'url\((.*?)\)'
            pattern5 = ur'src="./(.*?)"'
            l1 = re.findall(pattern, content)
            l2 = re.findall(pattern2, content)
            l4 = re.findall(pattern4, content)
            l5 = re.findall(pattern5, content)
            l3 = list(set(att_files) - (set(l1) | set(l2) | set(l4) | set(l5)))
            for m1 in l1:
                if m1 not in att_files:
                    continue
                file_path = os.path.join(save_path, m1)
                file_name, ufile_name, file_type, attachtype, file_size = handle_html_zip_attach(template_id, file_path, tpl_attachtype)
                link = u'src="{}?id={}&ufile_name={}&aid=1"'.format(_get_pic_url() + '/template/ajax_get_network_attach/', template_id, ufile_name)
                content = content.replace(u'src="{}"'.format(m1), link)
                att_obj = SendAttachment(user_id=request.user.id, template_id=template_id, filename=file_name, filetype=file_type, filepath=ufile_name, attachtype='html')
                att_obj.save()
            for m2 in l2:
                if m2 not in att_files:
                    continue
                file_path = os.path.join(save_path, m2)
                file_name, ufile_name, file_type, attachtype, file_size = handle_html_zip_attach(template_id, file_path, tpl_attachtype)
                link = u"url('{}?key={},1,{}')".format(_get_pic_url() + '/template/ajax_get_netatt/', template_id, ufile_name)
                content = content.replace(u"url('{}')".format(m2), link)
                att_obj = SendAttachment(user_id=request.user.id, template_id=template_id, filename=file_name, filetype=file_type, filepath=ufile_name, attachtype='html')
                att_obj.save()

            for m4 in l4:
                if m4 not in att_files:
                    continue
                file_path = os.path.join(save_path, m4)
                file_name, ufile_name, file_type, attachtype, file_size = handle_html_zip_attach(template_id, file_path, tpl_attachtype)
                link = u"url({}?key={},1,{})".format(_get_pic_url() + '/template/ajax_get_netatt/', template_id, ufile_name)
                content = content.replace(u"url({})".format(m4), link)
                att_obj = SendAttachment(user_id=request.user.id, template_id=template_id, filename=file_name, filetype=file_type, filepath=ufile_name, attachtype='html')
                att_obj.save()

            for m5 in l5:
                if m5 not in att_files:
                    continue
                file_path = os.path.join(save_path, m5)
                file_name, ufile_name, file_type, attachtype, file_size = handle_html_zip_attach(template_id, file_path, tpl_attachtype)
                link = u'src="{}?id={}&ufile_name={}&aid=1"'.format(_get_pic_url() + '/template/ajax_get_network_attach/', template_id, ufile_name)
                content = content.replace(u'src="./{}"'.format(m5), link)
                att_obj = SendAttachment(user_id=request.user.id, template_id=template_id, filename=file_name, filetype=file_type, filepath=ufile_name, attachtype='html')
                att_obj.save()

            for m3 in l3:
                file_path = os.path.join(save_path, m3)
                file_name, ufile_name, file_type, attachtype, file_size = handle_html_zip_attach(template_id, file_path, tpl_attachtype, attachtype='common')
                attachsize = 0
                if attachtype == "common":
                    attachsize = file_size
                att_obj = SendAttachment(
                    user_id=request.user.id, template_id=template_id, filename=file_name,
                    filetype=file_type, filepath=ufile_name, attachtype=attachtype, size=attachsize
                )
                att_obj.save()
                if attachtype == 'html':
                    ajax_url = _get_pic_url() + '/template/ajax_get_network_attach/'
                    file_size = filesizeformat(file_size)
                    content = get_html_content(content, ajax_url, template_id, ufile_name, file_type, file_name, file_size)

            try:
                del_filepath(save_path)
            except:
                pass
        else:
            try:
                del_filepath(save_path)
            except:
                pass
            msg = {'status': 'N', 'msg': _(u'压缩文件组成结构不正确')%{}, 'content': ''}
            return HttpResponse(json.dumps(msg), content_type="application/json")
        django_html = obj.render_attach_template()
        msg = {'status': 'Y', 'msg': _(u'提交成功')%{}, 'content': content, 'attach': django_html, 'edit_type': '5'}
        return HttpResponse(json.dumps(msg), content_type="text/plain")
        # return HttpResponse(json.dumps(msg), content_type="application/json")

# 附件 提交
@csrf_exempt
# @login_required
def ajax_multi_upload(request, template_id):
    attachfile = request.FILES.get('filedata', None)
    if not attachfile:
        return HttpResponse(json.dumps({'status': 'N'}), content_type="application/json")
    user_id = request.GET.get('user_id', '')
    try:
        obj = SendTemplate.objects.get(user_id=user_id, pk=template_id)
    except:
        return HttpResponse(json.dumps({'status': 'N'}), content_type="application/json")
    attachtype = obj.attachtype if obj.attachtype else 'common'

    try:
        file_type = attachfile.content_type
        attachsize = attachfile.size
        suffix = attachfile.name.split('.')[-1]
        if suffix.lower() not in UPLOAD_ALLOWED_SUFFIX:
            return HttpResponse(json.dumps({'status': 'S'}), content_type="application/json")
        if suffix in UPLOAD_JSON_SUFFIX['image'] and (file_size_conversion(attachsize, MB) > 1):
            return HttpResponse(json.dumps({'status': 'M', 'message': _(u'上传图片不能大于1M！')%{}}), content_type="application/json")
        attachsize = attachsize if attachtype == "common" else 0
        file_name, ufile_name = handle_uploaded_attachfile(template_id, attachfile)
        att_obj = SendAttachment(
            user_id=user_id, template_id=template_id, filename=file_name,
            filetype=file_type, filepath=ufile_name, attachtype=attachtype, size=attachsize
        )
        att_obj.save()
        obj.content_type = 1
        obj.save()
        if attachtype == 'html':
            ajax_url = _get_pic_url() + '/template/ajax_get_network_attach/'
            file_size = filesizeformat(attachfile.size)
            appendto_content = get_html_content('', ajax_url, template_id, ufile_name, file_type, file_name, file_size)
            return HttpResponse(json.dumps({'status': 'H', 'appendto_content': appendto_content}), content_type="application/json")
        else:
            appendto_attchlist =u'''
            <li style="background: #EFEFEF;" id="id_attach_li_{0}" class="padding-5 margin-top-5">
                <a href="/template/ajax_download_attachfile/{1}/{0}/" target="_blank">{2}</a>
                <small class="text-muted">({3})</small>
                <span class="margin-left-5">
                    <a onclick="Javascript:delAttachment({0},{1})"class="myself-txt-color-red">X</a>
                </span>
            </li>
            '''.format(att_obj.id, template_id, file_name, filesizeformat(attachsize))
            return HttpResponse(json.dumps({'status': 'C','appendto_attchlist': appendto_attchlist}), content_type="application/json")
    except BaseException as e:
        return HttpResponse(json.dumps({'status': 'F'}), content_type="application/json")


# 附件 提交
@csrf_exempt
@login_required
def ajax_attachfile_upload(request, template_id):
    try:
        obj = get_object(SendTemplate, request.user, template_id)
        data = request.POST
        if not data:
            data = request.GET
        attachtype = data.get('attachtype', '')
        if not attachtype:
            attachtype = 'common'
        user_id = request.user.id
        attachfile = request.FILES.get('attachfile', None)
        file_type = attachfile.content_type
        attachsize = attachfile.size
        suffix = attachfile.name.split('.')[-1]
        if suffix in UPLOAD_JSON_SUFFIX['image'] and (file_size_conversion(attachsize, MB) > 1):
            return HttpResponse(json.dumps({'status': 'N', 'message': _(u'<small class="myself-txt-color-green">上传图片不能大于1M！</small>')%{}}), content_type="application/json")
        elif (file_size_conversion(attachsize, MB) > 10):
            return HttpResponse(json.dumps({'status': 'N', 'message': _(u'<small class="myself-txt-color-green">上传文件不能大于10M！</small>')%{}}), content_type="application/json")
        attachsize = attachsize if attachtype == "common" else 0
        file_name, ufile_name = handle_uploaded_attachfile(template_id, attachfile)
        att_obj = SendAttachment(
            user_id=user_id, template_id=template_id, filename=file_name,
            filetype=file_type, filepath=ufile_name, attachtype=attachtype, size=attachsize
        )
        att_obj.save()
        obj.content_type = 1
        obj.save()

        appendto_content, appendto_attchlist = '', ''
        if attachtype == 'html':
            ajax_url = _get_pic_url() + '/template/ajax_get_network_attach/'
            file_size = filesizeformat(attachfile.size)
            appendto_content = get_html_content('', ajax_url, template_id, ufile_name, file_type, file_name, file_size)
        else:
            lists = []
            field = ('id', 'filename', 'template_id', 'size')
            lists.append(dict(zip(field,(att_obj.id, file_name, template_id, attachsize))))
            html = get_render_attach_template()
            t = template.Template(html)
            appendto_attchlist = t.render(Context({'lists': lists}))
        msg = {'status': 'Y', 'message': _(u'提交成功')%{}, 'appendto_content': appendto_content, 'appendto_attchlist': appendto_attchlist}
        return HttpResponse(json.dumps(msg), content_type="application/json")
    except BaseException as e:
        print e
        return HttpResponse(json.dumps({'status': 'N', 'message': _(u'<small class="myself-txt-color-green">提交异常,请重试</small>')%{}}), content_type="application/json")

# 删除 传统附件
@csrf_exempt
@login_required
def ajax_delete_attach_id(request):
    data = request.POST
    template_id = int(data.get('template_id', ''))
    attach_id = int(data.get('attach_id', ''))
    obj = SendTemplate.objects.get(id=template_id, user=request.user)
    obj.delete_attach(attachtype='common', attach_id=attach_id)
    return HttpResponse("Y", content_type="text/plain")

# 下载 附件
@csrf_exempt
@login_required
def ajax_download_attachfile(request, template_id, attach_id):
    obj = get_object(SendAttachment, request.user, attach_id)
    file_path = os.path.join(ATTACH_SAVE_PATH, str(template_id), obj.filepath)
    with open(file_path, 'r') as f:
        content = f.read()
    response = HttpResponse(content, content_type=obj.filetype)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(obj.filename.encode('utf-8'))
    return response

# eml导入时，网络附件链接
def ajax_get_network_attach(request):
    template_id = int(request.GET.get('id', '').strip())
    ufile_name = request.GET.get('ufile_name', '').strip()
    # file_type = request.GET.get('file_type', '')
    # file_name = request.GET.get('file_name', '')
    aid = request.GET.get('aid', '')
    download = request.GET.get('download', '')
    lists = SendAttachment.objects.filter(template_id=template_id, filepath=ufile_name)
    if not lists:
        raise Http404
    file_type = lists[0].filetype
    file_name = lists[0].filename
    file_name = file_name.replace(u"    ", "").replace(u" ", "")
    # import sys
    # print >>sys.stderr, '--------------------', file_name, type(file_name)
    if template_id and ufile_name and file_type:
        file_path = os.path.join(ATTACH_SAVE_PATH, str(template_id), ufile_name)
        with open(file_path, 'r') as f:
            content = f.read()
        if aid:
            response = HttpResponse(content, content_type=file_type)
        if download:
            try:
                file_name = file_name.encode('utf-8')
            except:
                file_name = file_name.encode('cp936')
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
            if user_agent.find('firefox') == -1:
                file_name = urllib.quote_plus(file_name)

            response['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name)
            # response['Content-Disposition'] = 'attachment; filename="{}"'.format(Header(file_name, 'utf-8'))
        return response
    else:
        raise Http404

def ajax_get_netatt(request):
    key = request.GET.get('key', '').strip()
    template_id, aid, ufile_name = key.split(',')
    lists = SendAttachment.objects.filter(template_id=template_id, filepath=ufile_name)
    if not lists:
        raise Http404
    file_type = lists[0].filetype
    file_name = lists[0].filename
    if template_id and ufile_name and file_type:
        file_path = os.path.join(ATTACH_SAVE_PATH, str(template_id), ufile_name)
        with open(file_path, 'r') as f:
            content = f.read()
        if aid:
            response = HttpResponse(content, content_type=file_type)
        return response
    else:
        raise Http404

# 检查HTML内容语言, 目前判断还存在问题(已作废)
@csrf_exempt
@login_required
def ajax_check_template_lang(request):
    data = request.POST
    content = data.get('content', '')
    content = delhtml2text(content)
    m = re.search(ur'[\u4e00-\u9fa5]+', content)
    lang = 'cn' if m else 'en'
    if lang == 'cn':
        try:
            content.encode('GB2312')
            lang = 'zh'
        except UnicodeEncodeError:
            lang = 'tw'
    if lang == 'en':
        m = re.search(ur'[\xAC00-\xD7A3]+', content)
        if m:
            lang = 'ko'
        # 日文判断
        m = re.search(ur'[\u0800-\u4e00]+', content)
        if m:
            lang = 'ja'
    return HttpResponse(lang, content_type="text/plain")

# html代码替换为纯文本
@csrf_exempt
@login_required
def ajax_del_html_to_text(request):
    try:
        data = request.POST
        content = data.get('content', '')
        text = delhtml2text(content)
        msg = {'status': 'Y', 'msg': _(u'获取成功')%{}, 'text_content': text}
        return HttpResponse(json.dumps(msg), content_type="application/json")
    except BaseException as e:
        print e
        return HttpResponse(json.dumps({'status': 'N', 'msg': _(u'异常,请重试')%{}}), content_type="application/json")

from app.utils.response import get_language_unsubscribe_response, get_language_complaint_response

# 退订邮件（mode=0）、订阅邮件（mode=1）、投诉（mode=2）
def ajax_unsubscribe_or_complaints(request):
    data = request.GET
    mailist = data.get('mailist', '').strip()
    recipents = data.get('recipents', '').strip()
    mode = data.get('mode', '').strip()
    cr = connections['mm-pool'].cursor()
    p = re.compile('^(\w|[-+=.])+@\w+([-.]\w+)*\.(\w+)$')
    if mode == '0':
        if p.match(recipents):
            try:
                mailist_list = mailist.split('_')
                if len(mailist_list) == 1:
                    mailist_id = mailist_list[0]
                    obj = MailList.objects.get(id=mailist_id)
                    user_id = obj.customer_id
                else:
                    user_id, mailist_id = mailist_list
                    obj = MailList.objects.get(id=mailist_id)
                    user_id = obj.customer_id
                tablename = 'ml_unsubscribe_' + str(user_id)
                tablename_2 = 'ml_subscriber_' + str(user_id)
                if not _select_fetchone(cr, tablename, mailist_id, recipents):
                    cr.execute("INSERT INTO {0} (list_id, address, datetime) VALUES ({1}, '{2}', now());".format(tablename, mailist_id, recipents))
                if _select_fetchone(cr, tablename_2, mailist_id, recipents):
                    cr.execute("DELETE FROM {0} WHERE address='{1}' AND list_id={2};".format(tablename_2, recipents, mailist_id))
            except:
                print >>sys.stderr, traceback.format_exc()
        return get_language_unsubscribe_response(request)
        response = HttpResponse('退订成功！  (Successfully unsubscribed!)')
    elif mode == '2':
        # http://4zy9xnsn5.count.bestedm.org/template/ajax_unsubscribe_or_complaints/?mailist=2369_745333&amp;recipents={RECIPIENTS}&amp;mode=2&amp;
        # template_id=228510&amp;user_id=2369&amp;send_id=885293&amp;subject={SUBJECT_STRING}
        # http://192.168.1.24:8090/template/ajax_unsubscribe_or_complaints/?mailist={MAILLIST_ID}&recipents={RECIPIENTS}&mode=2&template_id=163058&user_id=2369&task_id={TASK_ID}&subject={SUBJECT}
        template_id = data.get('template_id', None)
        user_id = data.get('user_id', None)
        task_id = data.get('send_id', None)
        subject = data.get('subject', '').strip()
        mailist_list = mailist.split('_')
        if len(mailist_list) == 1:
            mailist_id = mailist_list[0]
            obj = MailList.objects.get(id=mailist_id)
            user_id = obj.customer_id
        else:
            try:
                user_id, mailist_id = mailist_list
                obj = MailList.objects.get(id=mailist_id)
                user_id = obj.customer_id
            except:
                user_id = None
        if user_id and p.match(recipents):
            try:
                _exsist = ComplaintList.objects.filter(address=recipents).exists()
                if not _exsist:
                    ComplaintList.objects.create(
                        address=recipents, customer_id=user_id, template_id=template_id, subject=subject, task_id=task_id
                    )
                cr.execute("UPDATE ml_subscriber_{} SET is_subscribe=%s WHERE address=%s AND list_id=%s;".format(user_id), (2, recipents, mailist_id))
                redis = get_redis_connection()
                redis.rpush("edm_web_user_mail_import_count_queue", '{}_{}'.format(user_id, mailist_id))
            except BaseException as e:
                print >>sys.stderr, traceback.format_exc()
        return get_language_complaint_response(request)
        response = HttpResponse('投诉成功！  (Successfully Complainted!)')
    else:
        response = HttpResponseForbidden('<h1>Forbidden</h1>')
    return response

def _select_fetchone(cr, tablename, mailist, recipents):
    cr.execute("SELECT address FROM {0} WHERE list_id={1} AND address='{2}';".format(tablename, mailist, recipents))
    return cr.fetchone()

# 无法正常显示
def ajax_recipient_view_template(request):
    data = request.GET
    recipents = data.get('recipents', '').strip()
    fullname = data.get('fullname', '').strip()
    send_id = data.get('send_id', '').strip()
    template_id = data.get('template_id', '').strip()
    try:
        objs = SendContent.objects.filter(send_id=send_id, template_id=template_id)

        obj = objs[0]
        user_id = obj.user_id
        list_id = obj.send.send_maillist_id

        content = obj.send_content.replace("\r\n", "\n").encode('utf-8')
        p = ParseEmail(content)
        data = p.parseMailTemplate()
        html_text = data.get('html_text', '')
        plain_text = data.get('plain_text', '')
        html_charset = data.get('html_charset', '')
        plain_charset = data.get('plain_charset', '')
        if html_text:
            html_text = html_text.decode(html_charset, 'ignore')
            html_text = show_mail_replace(user_id, template_id, send_id, list_id, recipents, fullname, html_text)
            html_text = html_text.encode(html_charset, 'ignore')
            response = HttpResponse(html_text, charset=html_charset)
        elif plain_text:
            response = HttpResponse(plain_text, charset=plain_charset)
    except BaseException as e:
        try:
            obj = SendTemplate.objects.get(id=template_id)
            charset = obj.character if obj.character else 'utf-8'
            response = HttpResponse(obj.content, charset=charset)
            return response
        except:
            raise Http404
    return response

# KindEditor 上传图片、附件  处理
@csrf_exempt
@login_required
def ajax_upload_json(request):
    try:
        data = request.GET
        template_id = int(data.get('template_id', ''))
        user_id = int(data.get('user_id', ''))
        dir = data.get('dir', '')
        imgFile = request.FILES.get('imgFile', None)
        obj = SendTemplate.objects.get(id=template_id, user=request.user)
        if not imgFile:
            return HttpResponse(json.dumps({'error': 1, 'url': '', 'message': _(u'请选择文件.')%{}}), content_type="text/plain")
            # return HttpResponse(json.dumps({'error': 1, 'url': '', 'message': u'请选择文件.'}), content_type="application/json")

        image_encode = obj.image_encode if obj.image_encode else 'Y'
        if dir == 'image' and image_encode == 'Y':
            file_type = imgFile.content_type
            # encoding = 'base64'
            content = imgFile.read()
            content = base64.b64encode(content)
            url = "data:{};base64,{}".format(file_type, content)
            return HttpResponse(json.dumps({'error': 0, 'url': url, 'message': ''}), content_type="text/plain")
            # return HttpResponse(json.dumps({'error': 0, 'url': url, 'message': ''}), content_type="application/json")
        else:
            file_name = imgFile.name
            suffix = file_name.split('.')[-1]
            if suffix.lower() not in UPLOAD_JSON_SUFFIX[dir]:
                return HttpResponse(json.dumps({
                    'error': 1,
                    'url': '',
                    'message': _(u"上传文件扩展名是不允许的扩展名。\n只允许 %(json_suffix)s 格式。") % {'json_suffix': ','.join(UPLOAD_JSON_SUFFIX[dir])},
                }), content_type="application/json")

            if (file_size_conversion(imgFile.size, MB) > 1):
                return HttpResponse(json.dumps({'error': 1, 'url': '', 'message': _(u'上传图片大小不能超过1M。')%{}}), content_type="text/plain")
                # return HttpResponse(json.dumps({'error': 1, 'url': '', 'message': u'上传图片大小不能超过1M。'}), content_type="application/json")

            file_type = imgFile.content_type
            file_name, ufile_name = handle_uploaded_attachfile(template_id, imgFile)
            att_obj = SendAttachment(user_id=user_id, template_id=template_id, filename=file_name, filetype=file_type, filepath=ufile_name, attachtype='html')
            att_obj.save()

            ajax_url = _get_pic_url() + '/template/ajax_get_network_attach/'
            if dir == 'image':
                url = u"{}?id={}&ufile_name={}&aid=1"
            else:
                url = u"{}?id={}&ufile_name={}&aid=1&download=1"
            url = url.format(ajax_url, template_id, ufile_name)
            return HttpResponse(json.dumps({'error': 0, 'url': url, 'message': ''}), content_type="text/plain")
            # return HttpResponse(json.dumps({'error': 0, 'url': url, 'message': ''}), content_type="application/json")
    except:
        return HttpResponse(json.dumps({'error': 1, 'url': '', 'message': _(u'上传异常，请重试。')%{}}), content_type="text/plain")
        # return HttpResponse(json.dumps({'error': 1, 'url': '', 'message': u'上传异常，请重试。'}), content_type="application/json")

# ajax 获取参考模板图片列表
@csrf_exempt
@login_required
def ajax_get_ref_template_imglist(request):
    data = request.GET
    cate_id = int(data.get('cate_id', 0))
    page = int(data.get('page', 1))
    lists = RefTemplate.objects.filter(status=1)
    if cate_id:
        lists = RefTemplate.objects.filter(cate_id=cate_id, status=1)
    lists = lists.order_by('id')
    per_page = 7
    orphans = 0 # 设置最后至少要有多少个数，才不移到前面

    paginator = Paginator(lists, per_page, orphans)
    try:
        lists = paginator.page(page)
    except PageNotAnInteger:
        lists = paginator.page(1) # If page is not an integer, deliver first page.
    except EmptyPage:
        lists = paginator.page(paginator.num_pages) # If page is out of range (e.g. 9999), deliver last page of results.
    # t = TemplateResponse(request, 'template/render_ref_template_imglist.html', {'lists': lists})
    # t.render()
    # django_html = t.content
    html = get_render_refimg_template()
    t = template.Template(html)
    django_html = t.render(Context({'lists': lists, 'img_url': settings.REF_TPL_IMG_URL}))
    return HttpResponse(django_html, content_type="text/html")

# ajax 参考模板覆盖 HTML内容
@csrf_exempt
@login_required
def ajax_reftemplate_cover_htmlcontent(request):
    data = request.GET
    template_id = int(data.get('template_id', 0))
    obj = RefTemplate.objects.get(id=template_id)
    content = obj.content
    return HttpResponse(content, content_type="text/html")
