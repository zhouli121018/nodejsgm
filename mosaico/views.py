# -*- coding: utf-8 -*-
#
import re
import json
import time
from urlparse import urlsplit

from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
from django.db.transaction import atomic
from django_redis import get_redis_connection

from premailer import transform
from PIL import Image, ImageDraw

from app.mosaico.models import Upload, Template
from app.mosaico import tools
from app.mosaico.img import get_placeholder_image
from app.template.models import SendTemplate, SendSubject

from app.template.configs import ( EDIT_TYPE, CONTENT_TYPE, ENCODING_TYPE, CHARACTER_TYPE, IMAGE_TYPE, ATTACH_TYPE, PRIORITY_TYPE )
from lib.common import get_object
from django.utils.translation import ugettext_lazy as _
from django.db import connections
from app.template.utils import commons

@login_required
def create(request):
    if request.method == "POST":
        mosaico_name = request.POST.get("mosaico_name", "")
        mosaico_name = mosaico_name or "versafix-1"
        mosaico_status = request.POST.get("mosaico_status", "")
        if mosaico_status == "create":
            with atomic():
                tpl_obj = SendTemplate.objects.create(
                    user=request.user, content_type=1, encoding='base64', character='utf-8',
                    image_encode='N', attachtype='html', priority='low', status='0', isvalid=1, issync=0,
                    is_mosaico=True
                )
                template_id = tpl_obj.id
                key = tools.get_mosaico_key(template_id)
                created = int(time.time())
                first = Template.objects.filter(user_id=request.user.id, template_id=template_id).first()
                if not first:
                    if mosaico_name == "versafix-1":
                        name = "versafix-1"
                        tpl_default = tools.VersafixSettings()
                        meta_data = {
                            "key": key,
                            "name": "versafix-1",
                            "created": created,
                            "editorversion": "0.15.0",
                            "template": "/static/mosaico/templates/versafix-1/template-versafix-1.html",
                            "templateversion": "1.0.5"
                        }
                    else:
                        name = "tedc15"
                        tpl_default = tools.Tedc15Settings()
                        meta_data = {
                            "key": key,
                            "name": "tedc15",
                            "created": created,
                            "editorversion": "0.15.0",
                            "template": "/static/mosaico/templates/tedc15/template-tedc15.html",
                        }

                    template, _created = Template.objects.get_or_create(
                        # key=key,
                        name=name,
                        user_id=request.user.id,
                        template_id=template_id,
                    )
                    template.html = tpl_default.DEFAULT_HTML
                    template.template_data = tpl_default.TEMPLATE_DATA
                    template.meta_data = meta_data
                    template.save()
            return HttpResponseRedirect(reverse("mosaico_template_modify", args=(template_id,)))
    return HttpResponseRedirect(reverse("home"))

def get_original(obj, user_id):
    if not obj.is_mosaico:
        return Http404
    template_id = obj.id
    key = tools.get_mosaico_key(template_id)
    original = Template.objects.filter(user_id=user_id, template_id=template_id).first()
    if not original:
        name = "versafix-1"
        created = int(time.time())
        tpl_default = tools.VersafixSettings()
        meta_data = {
            "key": key,
            "name": "versafix-1",
            "created": created,
            "editorversion": "0.15.0",
            "template": "/static/mosaico/templates/versafix-1/template-versafix-1.html",
            "templateversion": "1.0.5"
        }
        original, _created = Template.objects.get_or_create(
            # key=key,
            name=name,
            user_id=user_id,
            template_id=template_id,
        )
        original.html = tpl_default.DEFAULT_HTML
        original.template_data = tpl_default.TEMPLATE_DATA
        original.meta_data = meta_data
        original.save()
    return original

@login_required
def template_modify(request, template_id):
    obj = get_object(SendTemplate, request.user, template_id)
    original = get_original(obj, request.user.id)
    if request.method == "POST":
        data = request.POST
        name = data.get('name', '')
        encoding = data.get('encoding', 'base64')
        character = data.get('character', 'utf-8')

        subject_list = data.getlist('subject_list[]', '')
        SendSubject.objects.filter(template_id=template_id).delete()
        subject_obj_list, template_subject = [], ''
        for subject in subject_list:
            if subject:
                template_subject = subject
                subject_obj_list.append(SendSubject(template_id=template_id, subject=subject))
        SendSubject.objects.bulk_create(subject_obj_list)

        obj.name = name
        obj.subject = template_subject
        obj.encoding = encoding
        obj.character = character
        obj.issync = True
        # obj.result = None
        obj.save()
        return HttpResponseRedirect(reverse("mosaico_start", args=(template_id,)))
    lang_code = request.user.lang_code
    cr = connections['mm-pool'].cursor()
    subject_vals, content_vals = commons.getVars(cr, request.user.id, lang_code)
    subject_objs = SendSubject.objects.filter(template_id=template_id)
    return render(request, template_name='mosaico/modify.html', context={
        'template_obj': obj,
        'subject_objs': subject_objs,
        'subject_vars': subject_vals,
        'encoding_types': ENCODING_TYPE,
        'character_types': CHARACTER_TYPE,
        'attachtype_types': ATTACH_TYPE,
        "original": original,
    })

@login_required
def start(request, template_id):
    obj = get_object(SendTemplate, request.user, template_id)
    original = get_original(obj, request.user.id)

    lang_code = request.user.lang_code
    cr = connections['mm-pool'].cursor()
    subject_vals, content_vals = commons.getVars(cr, request.user.id, lang_code)
    return render(request, 'mosaico/start.html', context={
        "original": original,
        "template_id": template_id,
        "subject_vals": json.dumps(dict(subject_vals)),
        "subject_list": json.dumps([key for key, value in subject_vals])
    })

@csrf_exempt
@login_required
def get(request, template_id):
    return HttpResponse(json.dumps({"STATUS": True}), content_type="application/json")

@login_required
def index(request):
    return render(request, 'mosaico/index.html')

@csrf_exempt
@login_required
def template(request):
    action = request.POST['action']
    if action == 'save':
        user_id = request.user.id
        key = request.POST['key']
        template_id = tools.get_template_id(key)
        # name = request.POST['name']
        html = request.POST['html']
        template_data = json.loads(request.POST['template_data'])
        meta_data = json.loads(request.POST['meta_data'])
        try:
            obj = Template.objects.get(user_id=user_id, template_id=template_id)
        except:
            return HttpResponse("unknown action", status=400)

        html = tools.replace_template(template_id, html)
        print(html)
        obj.html = html
        obj.template_data = template_data
        obj.meta_data = meta_data
        obj.save()

        tpl_obj = SendTemplate.objects.get(id=template_id)
        tpl_obj.content = html
        tpl_obj.text_content = tools.TEXT_CONTENT
        tpl_obj.issync = True
        tpl_obj.result = None
        tpl_obj.save()

        # redis = get_redis_connection()
        # redis.rpush('template_check', obj.id)
        # redis.rpush('edm_web_mail_template_point_queue', json.dumps({
        #     "user_id": tpl_obj.user_id,
        #     'template_id': obj.template_id,
        # }))

        redis = get_redis_connection()
        redis.rpush('template_check', template_id)
        redis.rpush('edm_web_mail_template_point_queue', json.dumps({
            "user_id": user_id,
            'template_id': template_id,
        }))

        messages.add_message(request, messages.SUCCESS, _(u"模板修改成功"))
        return HttpResponseRedirect('/template/?isvalid=1')
        # response = HttpResponse("template saved", status=201)
    else:
        response = HttpResponse("unknown action", status=400)
    return response

@csrf_exempt
@login_required
def download(request):
    html = transform(request.POST['html'])
    action = request.POST['action']
    if action == 'download':
        filename = request.POST['filename']
        content_type = "text/html"
        content_disposition = "attachment; filename=%s" % filename
        response = HttpResponse(html, content_type=content_type)
        response['Content-Disposition'] = content_disposition
    elif action == 'email':
        to = request.POST['rcpt']
        subject = request.POST['subject']
        from_email = settings.DEFAULT_FROM_EMAIL
        # TODO: convert the HTML email to a plain-text message here.  That way
        # we can have both HTML and plain text.
        msg = ""
        send_mail(subject, msg, from_email, [to], html_message=html, fail_silently=False)
        # TODO: return the mail ID here
        response = HttpResponse("OK: 250 OK id=12345")
    return response


@csrf_exempt
@login_required
def upload(request, user_id):
    if request.method == 'POST':
        upload = Upload.imgsave(user_id, request.FILES.values()[0])
        uploads = [upload]
    else:
        uploads = Upload.objects.filter(user_id=user_id).order_by('-id')
    data = {'files': []}
    for upload in uploads:
        data['files'].append(upload.to_json_data())
    response = HttpResponse(json.dumps(data), content_type="application/json")
    return response


# @csrf_exempt
def image(request):
    # print "request.method: ", request.method
    # print '------------------'
    if request.method == 'GET':
        method = request.GET['method']
        # print "method: ", method
        params = request.GET['params'].split(',')
        # print "params: ", params
        # print '--------------',method, params
        if method == 'placeholder':
            height, width = [tools.get_size(p) for p in params]
            image = get_placeholder_image(height, width)
            response = HttpResponse(content_type="image/png")
            image.save(response, "PNG")
        elif method == 'cover':
            src = request.GET['src']
            path = urlsplit(src).path
            width, height = [tools.get_size(p) for p in params]
            abspath = path.replace(settings.MEDIA_URL, "")
            upload = None

            for upload in Upload.objects.filter(image=abspath):
                if upload.absurl == path:
                    break
            if upload is None:
                height, width = [tools.get_size(p) for p in params]
                image = get_placeholder_image(height, width)
                response = HttpResponse(content_type="image/png")
                image.save(response, "PNG")
            else:
                image = Image.open(upload.filepath)
                image.thumbnail((width, height), Image.ANTIALIAS)
                response = HttpResponse(content_type="image/%s" % image.format.lower())
                image.save(response, image.format)
        elif method == 'resize' or method == 'cover':
            src = request.GET['src']
            path = urlsplit(src).path
            width, height = [tools.get_size(p) for p in params]
            abspath = path.replace(settings.MEDIA_URL, "")

            upload=None
            for upload in Upload.objects.filter(image=abspath):
                if upload.absurl == path:
                    break

            if upload is None:
                height, width = [tools.get_size(p) for p in params]
                image = get_placeholder_image(height, width)
                response = HttpResponse(content_type="image/png")
                image.save(response, "PNG")
            else:
                image = Image.open(upload.filepath, 'r')
                if not width:
                    width = image.width
                if not height:
                    height = image.height
                image.thumbnail((width, height), Image.ANTIALIAS)
                response = HttpResponse(content_type="image/%s" % image.format.lower())
                image.save(response, image.format)
        return response
