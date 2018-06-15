# -*- coding: utf-8 -*-

import os
import uuid
import json
import random
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.db import connections
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from app.template.models import SendTemplate, SendAttachment, RefTemplateCategory, RefTemplate
from app.task.models import SendContent
from app.template.forms import SendTemplateForm
from app.template.utils import commons
from app.template.utils import caches
from app.template.configs import UPLOAD_JSON_SUFFIX, MB
from lib.common import get_object
from lib.template import create_filepath
from lib.tools import file_size_conversion
from lib.parse_email import ParseEmail
from app.template.tools import show_mail_replace
from app.template.utils.email import addEmailTitle

@login_required
def template_add(request, template_id):
    obj = get_object(SendTemplate, request.user, template_id)
    if not obj.isvalid:
        raise Http404
    form = SendTemplateForm(request.user, template_id, instance=obj)
    if request.method == "POST":
        subject_list = request.POST.getlist('subject_list', '')
        form = SendTemplateForm(request.user, template_id, subject_list, request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            form.saveSubject(obj)
            caches.pushCheck(request.user.id, template_id)
            messages.add_message(request, messages.SUCCESS, _(u'模板修改成功'))
            next_uri = "{}?isvalid=1".format(reverse("template_list"))
            return HttpResponseRedirect(next_uri)
    reflists = RefTemplateCategory.objects.all()
    cr = connections['mm-pool'].cursor()
    lang_code = request.user.lang_code
    subject_vals, content_vals = commons.getVars(cr, request.user.id, lang_code)
    conmmon_vals = commons.getCommons(lang_code)
    umail_vals = commons.getUnsubscibes(lang_code, request.user.id, template_id)
    share_link = commons.getShareLink(lang_code)
    return render(request, template_name='template/cktemplate.html', context={
        "form": form,
        "template_id": template_id,
        'subject_vars': subject_vals,
        'content_vals': json.dumps(content_vals),
        'conmmon_vals': json.dumps(conmmon_vals),
        'umail_vals': json.dumps(umail_vals),
        'share_link': json.dumps(share_link),
        'reflists': reflists,
        'attach_list': obj.render_attach_template(),
    })

## -------------------
# ckedit 图片上传
@csrf_exempt
@login_required
def ckupload(request, template_id):
    user = request.user
    get_object(SendTemplate, user, template_id)
    callback = request.GET.get("CKEditorFuncNum")
    if request.method == 'POST' and request.FILES['upload']:
        fileobj = request.FILES['upload']
        content_type = fileobj.content_type
        fname = fileobj.name
        fext = os.path.splitext(fname)[-1]
        if fext.lower()[1:] not in UPLOAD_JSON_SUFFIX["image"]:
            error = _(u"请上传正确的图片格式")
            res = u"<script>window.parent.CKEDITOR.tools.callFunction({},'', '{}');</script>".format(callback, error)
            return HttpResponse(res)
        if (file_size_conversion(fileobj.size, MB) > 1):
            error = _(u"上传图片大小不能超过1M")
            res = u"<script>window.parent.CKEDITOR.tools.callFunction({},'', '{}');</script>".format(callback, error)
            return HttpResponse(res)
        uuname = '{}-{}{}'.format(str(uuid.uuid1()), random.randint(1, 100000), fext)
        tplpath = os.path.join(settings.ATTACH_DATA_PATH, str(template_id))
        fpath = os.path.join(tplpath, uuname)
        create_filepath(tplpath)
        with open(fpath, 'w') as f:
            f.write(fileobj.read())
        SendAttachment.objects.create(
            user_id=user.id, template_id=template_id, filename=fname,
            filetype=content_type, filepath=uuname, attachtype='html')
        uri = "{}{}?id={}&ufile_name={}&aid=1&download=1".format(
            commons.getPicUrl(), reverse("ajax_get_network_attach"), template_id, uuname)
        res = r"<script>window.parent.CKEDITOR.tools.callFunction("+callback+",'"+uri+"', '');</script>"
        return HttpResponse(res)
    raise Http404()


# ajax 获取参考模板图片列表
@csrf_exempt
@login_required
def ajax_ref_template(request):
    data = request.GET
    cate_id = int(data.get('cate_id', 0))
    page = int(data.get('page', 1))
    lists = RefTemplate.objects.filter(status=1)
    if cate_id:
        lists = RefTemplate.objects.filter(cate_id=cate_id, status=1)
    lists = lists.order_by('id')
    per_page = 6
    orphans = 0 # 设置最后至少要有多少个数，才不移到前面

    paginator = Paginator(lists, per_page, orphans)
    try:
        lists = paginator.page(page)
    except PageNotAnInteger:
        lists = paginator.page(1) # If page is not an integer, deliver first page.
    except EmptyPage:
        lists = paginator.page(paginator.num_pages) # If page is out of range (e.g. 9999), deliver last page of results.
    t = TemplateResponse(request, 'template/ckref.html', {'lists': lists, 'img_url': settings.REF_TPL_IMG_URL})
    t.render()
    return HttpResponse(t.content, content_type="text/html")

def share(request):
    data = request.GET
    r = data.get('r', '').strip() # 收件箱
    f = data.get('f', '').strip() # 姓名
    s = data.get('s', '').strip() # 任务ID
    t = data.get('t', '').strip() # 模板ID
    uri = ""
    subject = u"分享-Share"
    if s and t:
        try:
            obj = SendTemplate.objects.filter(id=t).first()
            subject = obj and obj.subject or u"分享-Share"
            subject = show_mail_replace(html=subject)
        except:
            pass
        uri = "{}{}?r={}&s={}&t={}&f={}".format(
            commons.getPicUrl(), reverse("ajax_view_template"),
            r, s, t, f
        )
    return render(request, template_name='template/share.html', context={
        "uri": uri,
        "subject": subject,
    })

# 无法正常显示
def ajax_view_template(request):
    data = request.GET
    recipents = data.get('r', '').strip()
    recipents = ""
    fullname = data.get('f', '').strip()
    send_id = data.get('s', '').strip()
    template_id = data.get('t', '').strip()
    try:
        obj2 = SendTemplate.objects.filter(id=template_id).first()
        subject = obj2 and obj2.subject or u"分享-Share"
        subject = show_mail_replace(html=subject)
        title = u'<title>{}</title>'.format(subject)

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
            html_text = addEmailTitle(html_text, title)
            response = HttpResponse(html_text, charset=html_charset)
        elif plain_text:
            plain_text = addEmailTitle(plain_text, title)
            response = HttpResponse(plain_text, charset=plain_charset)
    except BaseException as e:
        try:
            obj = SendTemplate.objects.get(id=template_id)
            subject = obj.subject or u"分享-Share"
            subject = show_mail_replace(html=subject)
            title = u'<title>{}</title>'.format(subject)
            charset = obj.character if obj.character else 'utf-8'
            html = addEmailTitle(obj.content, title)
            response = HttpResponse(html, charset=charset)
            return response
        except:
            raise Http404
    return response

