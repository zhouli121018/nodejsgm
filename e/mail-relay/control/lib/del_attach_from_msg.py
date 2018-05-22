# !/usr/local/u-mail/app/engine/bin/python
# -*-coding:utf8-*-
#
import re
import copy
import datetime
import common
import base64
import email
common.init_django_enev()

from apps.mail.models import get_mail_model, Settings
from apps.collect_mail.models import get_mail_model as get_mail_model2
from lib.parse_email import ParseEmail
from email.mime.text import MIMEText
from django import template
from django.template import Context
from django.conf import settings

def get_render_attchtemplate():
    html = u"""
    {% load static %}
    {% load mail_tags %}
    {% if m.real_attachments %}
    <div style="float: left; background:#fff;padding:2px; font-family: 'lucida Grande',Verdana,'Microsoft YaHei'; height: auto; border: 1px solid #d5d5d5; margin-bottom: 10px;">
        <ul style="list-style-type:none;padding:0px; margin:0px; float: left;">
            <li style="float: left;margin: 0px 5px 0px 0px; display: inline;">
                <b style="font-size:14px;">网络附件</b>
                <span style="font-size: 12px; color:red;">({{ m.real_attachments|length }}个,&nbsp;过期时间:{{ expire_day|default_if_none:"" }})</span>
            </li>
            <br />
            <hr style=" height:1px;border:none;border-top:1px solid #d5d5d5;" />
            {% for attach in m.real_attachments %}
            <li style="float: left;margin: 0px 5px 5px 0px; display: inline;">
                <a href="https://www.mailrelay.cn/mail/dowload_mail_real_attachment?key={{ mail_obj.date_id|get_private_key }}&amp;id={{mail_obj.date_id|get_base64_key}}&amp;aid={{forloop.counter0|get_base64_key}}&amp;download=1"
                   target="_blank" unset="true" title="{{ attach.decode_name }}">
                    <ul style="list-style-type: none; float: left">
                        <li style="overflow-x: hidden;text-overflow: ellipsis;white-space:nowrap; max-width: 250px; float: left; text-decoration: underline;color: #393939;">
                            {{attach.decode_name}}
                        </li>
                        <span style="color: #d5d5d5;">&nbsp;({{ attach.size|filesizeformat }})</span>
                    </ul>
                </a>
            </li>
            {% endfor %}
        </ul>
    </div>
    <div style="clear: both;"></div>
    {% endif %}
    """
    return html

def get_django_template():
    attachment_django_template = u'''
    {% load static %}
    {% load mail_tags %}
    {% if m.real_attachments %}
    <br /><br />
    <div style="padding:2px;background: #e6eaf0;font-family: 'lucida Grande',Verdana,'Microsoft YaHei';">
        <div style="padding:6px 10px 10px 8px; text-align: left;">
            <div style="height:14px;">
                <b style="font-size:14px;">
                    <img src="https://www.mailrelay.cn/static/img/umailspace.gif" style="margin:-3px 2px 0 0;background:*background-position:0 0;width:23px;height:23px;padding: 0;
                    border: none;" align="absmiddle" border="0">附件</b><span style="font-size: 12px;">({{ m.real_attachments|length }}个)</span>
            </div>
        </div>
        <div style="padding:0 8px 6px 12px;background:#fff;_height:60px;line-height:140%;">
            <div style="padding-top:12px; padding-bottom:5px;clear: both;color: #a0a0a0;">
                <b style="font-size:14px;color:#000;font-weight:bold;">网络附件</b><span style="font-size: 12px; color:red;">(过期时间:{{ expire_day|default_if_none:"" }})</span>
            </div>
            {% for attach in m.real_attachments %}
            <div style="overflow: hidden;_zoom: 1;margin: 0;padding: 5px 2px;clear: both; margin: 5px 0 10px;min-height: 40px;margin: 2px 8px 0 0;margin-top: 2px;">
                <div style="float: left;margin: 2px 8px 0 0;">
                    <img style="width: 36px; height: 42px;" src="https://www.mailrelay.cn/static/img/download_11.gif">
                </div>
                <div style="margin-top: 1px;float: left; height: 42px;">
                    <span>{{attach.decode_name}}</span>
                    <span style="color: #a0a0a0;">&nbsp;({{ attach.size|filesizeformat }})</span>
                    <div style="margin-top: 2px;">
                        <a href="https://www.mailrelay.cn/mail/dowload_mail_real_attachment?key={{ mail_obj.date_id|get_private_key }}&amp;id={{mail_obj.date_id|get_base64_key}}&amp;aid={{forloop.counter0|get_base64_key}}&amp;download=1"
                           target="_blank" unset="true" style="text-decoration: none;"><span style="color: #3D5E86;">下载</span></a>
                        {% if attach.decode_name|preview_check %}
                        - <a href="https://www.mailrelay.cn/mail/dowload_mail_real_attachment?key={{ mail_obj.date_id|get_private_key }}&amp;id={{mail_obj.date_id|get_base64_key}}&aid={{forloop.counter0|get_base64_key}}"
                             target="_blank" unset="true" style="text-decoration: none;"><span style="color: #3D5E86;">预览</span></a>
                        {% endif %}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}
    '''
    return attachment_django_template

def decode_str(s, charset=None):
    if charset is not None:
        try:
            return s.decode(charset, 'replace')
        except Exception:
            return s.decode('utf-8', 'replace')
    else:
        try:
            return s.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return s.decode('gb18030')
            except UnicodeDecodeError:
                return s.decode('utf-8', 'replace')

def html_add_footer(html, footer):
    m = re.search(r'</\s*(body|html)>', html, re.IGNORECASE)
    if m is not None:
        s = m.start()
    else:
        s = len(html)
    return html[:s] + footer + html[s:]

def heml_add_header(html, header):
    m = re.search(r'<(body|html)\s*>', html, re.IGNORECASE)
    if m is not None:
        s = m.end()
    else:
        s = 0
    return html[:s] + header + html[s:]

def del_attach_ins(message):
    msg_ins = message._payload
    if not message.is_multipart():
        return message
    msg_ins_copy = copy.copy(msg_ins)
    for part in msg_ins_copy:
        if not part.is_multipart() and part.get_filename() and not part.has_key('Content-ID'):
            msg_ins.remove(part)
        if isinstance(part._payload, list):
            del_attach_ins(part)
    return message

def del_attach_from_msg(date_id, f='relay'):
    date, id = date_id.split(',')
    mail_obj = get_mail_model(date).objects.get(id=id) if 'relay' == f else get_mail_model2(date).objects.get(id=id)
    email_content = mail_obj.get_mail_content()
    message = email.message_from_string(email_content)
    s = Settings.objects.all()
    if s:
        days = s[0].back_days
    else:
        days = 10

    message = del_attach_ins(message)

    p = ParseEmail(email_content)
    data = p.parseMailTemplate()
    expire_day = (mail_obj.created + datetime.timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
    context = {'m': data, 'mail_obj': mail_obj, 'expire_day': expire_day}

    # attachment_django_template = get_django_template()
    attachment_django_template = get_render_attchtemplate()

    t = template.Template(attachment_django_template)
    django_html = t.render(Context(context))

    l = []
    for part in message.walk():
        if not part.is_multipart():
            content_type = part.get_content_type()
            filename = part.get_filename()
            if content_type == 'text/html' and filename is None:
                l.append(part)
    if django_html and len(l) > 0:
        part = l[0]
        payload = part.get_payload(decode=True)
        charset = part.get_content_charset()
        html = decode_str(payload, charset)

        # server = '{}'.format( getattr(settings, 'WEB_USER_SHENZHEN') )
        # key = base64.b64encode('MAILDOWNLOAD' + '_' + date_id.replace(',', '_'))
        # word = base64.b64encode(date_id.replace(',', '_'))
        # link = 'http://{}/mail/dowload_mail_real_attachment?key={}&id={}&cid=\g<cid>'.format(server, key, word)
        # html = re.sub('"cid:(?P<cid>.*?)"', link, html)        

        # html2 = html_add_footer(html, django_html)
        html2 = heml_add_header(html, django_html)
        payload2 = base64.b64encode(html2.encode('utf-8'))
        part.set_payload(payload2)
        del part['content-type']
        del part['content-transfer-encoding']
        part['content-type'] = 'text/html; charset="utf-8"'
        part['content-transfer-encoding'] = 'base64'
    elif django_html:
        if not message.is_multipart():
            payload = message.get_payload(decode=True)
            charset = part.get_content_charset()
            html = decode_str(payload, charset)
            # html2 = html_add_footer(html, django_html)
            html2 = heml_add_header(html, django_html)
            payload2 = base64.b64encode(html2.encode('utf-8'))
            message.set_payload(payload2)
            del message['content-type']
            del message['content-transfer-encoding']
            message['content-type'] = 'text/html; charset="utf-8"'
            message['content-transfer-encoding'] = 'base64'
        else:
            msg = MIMEText(django_html, 'html', 'utf-8')
            message.attach(msg)

    msg = message.as_string()
    with open('{}_del_attach'.format(mail_obj.get_mail_path()), 'w') as f:
        f.write(msg)
    return msg

