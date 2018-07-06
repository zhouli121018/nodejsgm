#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright (C)  2016 By Alex Yang.  All rights reserved.
@author : Alex Yang
@version: 1.0
@created: 2016-09-22
'''

import os
import re
import time
import shutil
import zipfile
import mimetypes
import urllib
import copy
import random
import uuid
import email
import smtplib
import string
from email.utils import formatdate
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMENonMultipart import MIMENonMultipart
from email import Encoders
import gevent
from email.header import Header
from django.conf import settings
from django import template
from django.template import Context

ATTACH_SAVE_PATH = settings.ATTACH_DATA_PATH
from .tools import safe_format

CHARS = string.lowercase + string.digits

### 解码 ###
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

### 编码 ###
def encode_str(s, charset=None):
    if charset is not None:
        try:
            return s.encode(charset, 'replace')
        except Exception:
            return s.encode('utf-8', 'replace')
    else:
        try:
            return s.encode('utf-8')
        except UnicodeEncodeError:
            try:
                return s.encode('gb18030')
            except UnicodeEncodeError:
                return s.encode('utf-8', 'replace')

def decode_encode_str(s):
    try:
        return decode_str(s)
    except:
        return encode_str(s).decode('utf-8')

def html_add_footer(html, footer):
    m = re.search(r'</\s*(body|html)>', html, re.IGNORECASE)
    if m is not None:
        s = m.start()
    else:
        s = len(html)
    return html[:s] + footer + html[s:]

#############################################
### html内容删除外部资源（css、js） ###
def del_jscss_from_html(html):
    html = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
    # html = re.sub(r'<style.*?</style>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<link .*?>', '', html, flags=re.DOTALL|re.IGNORECASE)
    return html

### 从url导入：将相对url替换成绝对url ###
def replace_srchref_from_html(url, url2, html):
    findall = re.findall(r'src="(.+?)"', html)
    p = re.compile(r'^((https|http|ftp|rtsp|mms)+://)+')
    for value in findall:
        if value.startswith('/') and not value.startswith('//'):
            html = re.sub(value, url2 + value, html)
        elif not value.startswith('//') and not p.search(value):
            html = re.sub(value, url + '/' + value, html)
    return html

### 从html导入：判断是否包含相对路径 ###
def clear_relative_url(html):
    findall = re.findall(r'src="(.+?)"', html)
    for value in findall:
        if value.startswith('/') and not value.startswith('//'):
            m = 'src="' + value + '"'
            html = re.sub(m, '', html)
    return html

### 获取附件列表渲染模板 ###
def get_render_attach_template():
    path = os.path.join(settings.BASE_DIR, 'app', 'template', 'templates', 'template', 'render_attch_list.html')
    with open(path) as f:
        html = f.read()
    return html

### 获取参考模板列表渲染模板 ###
def get_render_refimg_template():
    path = os.path.join(settings.BASE_DIR, 'app', 'template', 'templates', 'template', 'render_ref_template_imglist.html')
    with open(path) as f:
        html = f.read()
    return html

### 获取网络附件渲染模板 ###
def get_render_net_template():
    # <p style="text-align:center">
    att_html = u'''
    <span>附件：</span>
        <a href="{{ ajax_url }}?id={{ template_id }}&ufile_name={{ ufile_name }}&aid=1&download=1">{{ file_name }}</a>
    <span>({{ file_size }})</span>
    '''
    return att_html

### 获取HTML内容 ###
def get_html_content(content, ajax_url, template_id, ufile_name, file_type, file_name, file_size):
    att_html = get_render_net_template()
    vlas = {
        'ajax_url': ajax_url,
        'template_id': template_id,
        'ufile_name': ufile_name,
        'file_type': file_type,
        'file_name': file_name,
        'file_size': file_size,
    }
    t = template.Template(att_html)
    att_html = t.render(Context(vlas))
    content = html_add_footer(content, att_html)
    return content

#############################################
#创建指定目录
def create_filepath(path=None):
    if not os.path.exists(path):
        os.makedirs(path)
    return True

#删除指定目录下的文件以及文件夹
def del_filepath(path_list=None):
    path_list = path_list if isinstance(path_list, (list, tuple)) else [path_list]
    for path in path_list:
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path, True)
    return True

#############################################
### 附件处理 ###
def handle_uploaded_attachfile(template_id, file):
    file_name = file.name
    suffix = file_name.split('.')[-1]
    ufile_name = '{}.{}'.format(uuid.uuid1(), suffix)
    tpl_path = os.path.join(ATTACH_SAVE_PATH, str(template_id))
    file_path = os.path.join(tpl_path, ufile_name)
    create_filepath(tpl_path)
    with open(file_path, 'w') as f:
        f.write(file.read())
    return file_name, ufile_name

#############################################
### 模板类型html: eml文件上传保存 ###
### 模板类型html: zip文件上传保存 ###
### 模板类型eml： eml文件上传保存 ###
def handle_uploaded_file(template_id=None, file=None, path=None, suffix='txt'):
    create_filepath(path)
    file_path = os.path.join(path, '{}.{}'.format(template_id, suffix))
    dest = open(file_path, 'wb+')
    for chunk in file.chunks():
        dest.write(chunk)
    dest.close()
    return file.name

#############################################
### 模板类型html：获取eml文件内容 ###
### 模板类型eml：获取eml文件内容 ###
def handle_get_file(template_id, path):
    file_path = os.path.join(path, '{}.txt'.format(template_id))
    with open(file_path, 'r') as f:
        content = f.read()
    del_filepath(file_path)
    return content

#############################################
### 从eml导入：附件处理 ###
def handle_html_attach(template_id, attach, tpl_attachtype):
    file_name = attach.get('decode_name', '')
    suffix = file_name.split('.')[-1]
    ufile_name = '{}.{}'.format(uuid.uuid1(), suffix)
    file_type = attach.get('content_type', '').split(';')[0]
    attachtype = 'common'
    if tpl_attachtype == 'html' or 'content_id' in attach:
        attachtype = 'html'
    attachsize = 0
    if attachtype == 'common':
        attachsize = attach.get('size', 0)
    att_path = os.path.join(ATTACH_SAVE_PATH, str(template_id))
    file_path = os.path.join(att_path, ufile_name)
    create_filepath(att_path)
    with open(file_path, 'w') as f:
        f.write(attach['data'])
    return file_name, ufile_name, file_type, attachtype, attachsize

#############################################

### 模板类型html：解压zip文件 ###
def handle_get_rarfile(template_id, path):
    zipfile_path = os.path.join(path, '{}.rar'.format(template_id))
    save_path = os.path.abspath(os.path.join(path, str(template_id)))
    create_filepath(save_path)

    count = 0
    suffix = ('html', 'htm')

    import rarfile
    f = rarfile.RarFile(zipfile_path)
    html_file, att_files= '', []
    for name in f.namelist():
        try:
            utf8name = decode_str(name).encode('utf-8')
        except:
            utf8name = encode_str(name)
            #utf8name = utf8name.decode('utf-8')
        # 判断文件格式最多两层：一个html文件 和 文件夹
        if len(utf8name.split('/')) > 2:
            f.close()
            return '', [], ''

        file_path = os.path.join(save_path, utf8name)
        zip_path_name = os.path.dirname(utf8name)
        pathname = os.path.abspath(os.path.join(save_path, zip_path_name))
        # 第一层只有一个html文件
        if zip_path_name == '':
            # 获取html文件路径
            T = utf8name.split('.')
            if len(T)>=2:
                count += 1
                html_file = utf8name
                if T[-1] not in suffix:
                    f.close()
                    return '', [], ''
            else:
                continue

        if not os.path.exists(pathname) and zip_path_name!= '':
            os.makedirs(pathname)

        data = f.read(name)
        if not os.path.isdir(file_path):
            # 获取附件或者引用文件名路径
            if zip_path_name != '':
                att_files.append(utf8name)
            fo = open(file_path, "w")
            fo.write(data)
            fo.close
    if count != 1:
        f.close()
        return '', [], ''
    f.close()
    del_filepath(zipfile_path)
    return html_file, att_files, save_path

### 模板类型html：解压zip文件 ###
def handle_get_zipfile(template_id, path):
    zipfile_path = os.path.join(path, '{}.zip'.format(template_id))
    save_path = os.path.abspath(os.path.join(path, str(template_id)))
    create_filepath(save_path)

    count = 0
    suffix = ('html', 'htm')
    f = zipfile.ZipFile(zipfile_path, "r")
    html_file, att_files= '', []
    for name in f.namelist():
        try:
            utf8name = decode_str(name).encode('utf-8')
        except:
            utf8name = encode_str(name)
            #utf8name = utf8name.decode('utf-8')
        # 判断文件格式最多两层：一个html文件 和 文件夹
        if len(utf8name.split('/')) > 2:
            f.close()
            return '', [], ''

        file_path = os.path.join(save_path, utf8name)
        zip_path_name = os.path.dirname(utf8name)
        pathname = os.path.abspath(os.path.join(save_path, zip_path_name))
        # 第一层只有一个html文件
        if zip_path_name == '':
            count += 1
            # 获取html文件路径
            html_file = utf8name
            if utf8name.split('.')[-1] not in suffix:
                f.close()
                return '', [], ''

        if not os.path.exists(pathname) and zip_path_name!= '':
            os.makedirs(pathname)

        data = f.read(name)
        if not os.path.isdir(file_path):
            # 获取附件或者引用文件名路径
            if zip_path_name != '':
                att_files.append(utf8name)
            fo = open(file_path, "w")
            fo.write(data)
            fo.close
    if count != 1:
        f.close()
        return '', [], ''
    f.close()
    del_filepath(zipfile_path)
    return html_file, att_files, save_path

### 从zip导入：附件处理 ###
def handle_html_zip_attach(template_id, file_path, tpl_attachtype, attachtype='html'):
    file_name = file_path.split('/')[-1]
    suffix = file_name.split('.')[-1]
    ufile_name = '{}.{}'.format(uuid.uuid1(), suffix)
    file_type = mimetypes.guess_type(file_path)[0]

    if tpl_attachtype == 'html':
        attachtype = 'html'

    tpl_path = os.path.join(ATTACH_SAVE_PATH, str(template_id))
    create_filepath(tpl_path)
    dir_file_path = os.path.join(tpl_path, ufile_name)
    if isinstance(file_path, unicode):
        file_path = file_path.encode('utf-8')

    shutil.copyfile(file_path, dir_file_path)
    file_size = os.path.getsize(dir_file_path)
    return file_name, ufile_name, file_type, attachtype, file_size

#############################################
### 发送邮件模板 ###
def send_template(host='127.0.0.1', port=10027, use_ssl=None, sender='system@riskcontrol.com.cn', receiver=None, message=None):
    deliver_ip = None
    receive_ip = None
    try:
        with gevent.Timeout(120):
            if use_ssl:
                s = smtplib.SMTP_SSL(host, port)
            else:
                s = smtplib.SMTP(host, port)
            deliver_ip = s.sock.getsockname()[0]
            receive_ip = s.sock.getpeername()[0]
            s.sendmail(sender, receiver, message)
            s.quit()
            code, msg = 250, 'ok'
    except smtplib.SMTPResponseException as e:
        code, msg = e.smtp_code, e.smtp_error
    except smtplib.SMTPRecipientsRefused as e:
        senderrs = e.recipients
        code, msg = senderrs[receiver]
    except gevent.Timeout:
        code, msg = -1, u'发送超时'
    except BaseException as e:
        code, msg = -1, repr(e)
    return code, msg, deliver_ip, receive_ip

#############################################
# 账号密码发送邮件
def smtp_send_email(host=None, port=25, account=None, password=None, sender=None, receivers=None, message=None):
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(host, port)    # 25 为 SMTP 端口号
        smtpObj.login(account, password)
        smtpObj.sendmail(sender, receivers, message)
        code, msg = 250, 'ok'
    except smtplib.SMTPException:
        code, msg = -1, u"Error: 无法发送邮件"
    except BaseException as e:
        code, msg = -1, repr(e)
    return code, msg


#############################################
### 通过邮件模板构造一个可以发送html、纯文本、附件的邮件 ###
# html_comments_oneline = re.compile(r'\<!--[^[#][^\r\n]+?--\>')
# html_comments_oneline = re.compile(r'\<!--(.*?)--\>')

class MulTemplateEmail(object):
    def __init__(self, content_type=1, character='utf-8', encoding='base64',
                 template_id=0, mail_from=u'system@bestedm.org', mail_to=u'test@bestedm.org', reply_to=None, task_id=None, send_maillist_id=None,
                 subject='', content='', text_content=None,
                 attachment=None, user_id=0, replace=False, edm_check_result='',
                 is_need_receipt=False, track_domain=None, sys_track_domain=None):
        """
        :param content_type: 判断是eml格式发送，还是html编辑模式发送
        :param character:    设置发送编码(转换字符集)
        :param encoding:     设置邮件编码(附件编码)
        :param attachtype:   判断是传统附件common，还是在线附件html（在线附件则以网络附件发送）
        :param template_id:  暂时生成附件的保存路径
        :param mail_from:    发件人
        :param mail_to:      收件人
        :param subject:      主题
        :param content:      html内容
        :param text_content: 纯文本
        :param eml_content:  eml内容
        :param attachment:   附件信息，字典列表, 格式：[{'filepath': 'XXX', 'filetype': 'application/octet-stream', 'filename': 'xxx.txt', 'attachtype': 'html'},...]
        :param replace:      变量替换标志
        :return:             返回邮件信息
        """
        self.content_type = content_type
        if not character: character='utf-8'
        # if not encoding:  encoding='base64'
        if encoding not in ["base64", "quoted-printable"]:
            encoding = 'base64'
        self.character = character
        self.encoding = encoding
        self.template_id = template_id
        self.mail_from = mail_from
        self.mail_to = mail_to
        self.reply_to = reply_to
        self.edm_check_result = edm_check_result
        self.is_need_receipt = is_need_receipt
        self.track_domain = track_domain
        self.sys_track_domain = sys_track_domain

        self._common_kwargs()
        if not subject:
            subject = ''
        if not content:
            content = ''
        # m = html_comments_oneline.match(content)
        # if m:
        #     content = content.replace(m.group(), '', count=1)
        # content = html_comments_oneline.match(content)
        self._relace_subject(subject, replace)
        self._relace_content(content, replace, template_id, user_id, task_id, send_maillist_id)

        if not text_content:
            text_content = u'''如果邮件内容无法正常显示请以超文本格式显示HTML邮件！\n
            （If the content of the message does not display properly, please display the HTML message in hypertext format!）'''
        self.text_content = text_content
        self.attachment = attachment
        self.attachment_path = ATTACH_SAVE_PATH
        # self.msgAlternative = MIMEMultipart('alternative')
        self.message = MIMEMultipart('alternative')
        if user_id==2369:
            self.message['List-Unsubscribe'] = "<mailto:tony@ceshi.magvision.com?subject=unsubscribe>, <http://www.bestedm.org/>"

            # if user_id==2369:
            # self.message['List-Unsubscribe'] = Header("<mailto:1248644045@qq.com?subject=unsubscribe>", None)
            # self.message['List-Unsubscribe'] = Header("<mailto:1248644045@qq.com>", None)
            # self.message['List-Unsubscribe'] = Header("<https://www.ceshi.magvision.com/login?next=/>, <mailto:1248644045@qq.com?subject=unsubscribe>", None)

    def _replace(self, content, s, replace_s):
        content = content.replace(s, str(replace_s))
        content = content.replace(urllib.quote_plus(s), str(replace_s))
        return content

    def _common_kwargs(self):
        self.kwargs = {}
        self.kwargs.update(
            FULLNAME='', RECIPIENTS= '', DATE='', RANDOM_NUMBER='', SEX='', BIRTHDAY='', PHONE='', AREA='',
            VAR1='', VAR2='', VAR3='', VAR4='', VAR5='', VAR6='', VAR7='', VAR8='', VAR9='', VAR10='',
            JOKE='', MOTTO='', HEALTH='', SUBJECT_STRING='',
            TEMPLATE_ID='', USER_ID='', SEND_ID='', MAILLIST_ID='',
        )
        return

    def _relace_subject(self, subject, replace):
        if replace:
            subject = safe_format(subject, **self.kwargs)
        self.subject = subject
        return

    # 生成一个start-end　随机长度的字符
    def _make_rand_rand_chars(self, start=5, end=10):
        return "".join([random.choice(CHARS) for i in range(random.randint(start, end))])

    # 内容里面链接替换成客户的域名
    def _replace_href_domain(self, content):
        def encrypt_url(matched):
            domain = self.track_domain if self.track_domain else '{}.{}'.format(self._make_rand_rand_chars(), settings.TRACK_DOMAIN_DEFAULT)
            search_url = matched.group(1)
            if search_url.startswith('http://'):
                search_url2 = (search_url.replace('http://', '')).split('/')[0]
                search_url2 = 'http://{}'.format(search_url2)
                if search_url2 in self.sys_track_domain:
                    search_url = search_url.replace(search_url2, 'http://{}'.format(domain))
            return 'href="{}"'.format(search_url)
        return re.sub('href="?\'?([^"\'>]*)', encrypt_url, content)

    # 图片链接替换
    def _replace_src_domain(self, content):
        def encrypt_url(matched):
            domain = self.track_domain if self.track_domain else '{}.{}'.format(self._make_rand_rand_chars(), settings.TRACK_DOMAIN_DEFAULT)
            search_url = matched.group(1)
            if search_url.startswith('http://'):
                search_url2 = (search_url.replace('http://', '')).split('/')[0]
                search_url2 = 'http://{}'.format(search_url2)
                if search_url2 in self.sys_track_domain:
                    search_url = search_url.replace(search_url2, 'http://{}'.format(domain))
            return 'src="{}"'.format(search_url)
        return re.sub('src="?\'?([^"\'>]*)', encrypt_url, content)

    def _relace_content(self, content, replace, template_id, user_id, task_id, send_maillist_id):
        content = content.replace("\r\n", "\n")
        if template_id:
            content = self._replace(content, '{TEMPLATE_ID}', template_id)
        if user_id:
            content = self._replace(content, '{USER_ID}', user_id)
        if task_id:
            content = self._replace(content, '{SEND_ID}', task_id)
        if send_maillist_id is not None:
            content = self._replace(content, '{MAILLIST_ID}', '{}_{}'.format(user_id, send_maillist_id))
        if replace:
            content = self._replace(content, '{JOKE-MOTTO}', '')
            content = safe_format(content, **self.kwargs)
        if self.track_domain is not None:
            content = self._replace_href_domain(content)
            content = self._replace_src_domain(content)
        self.content = content
        return

    @staticmethod
    def encode_(s):
        try:
            return s.encode('utf-8')
        except UnicodeDecodeError:
            try:
                return s.encode('gb18030')
            except UnicodeDecodeError:
                return s.encode('utf-8', 'replace')

    @staticmethod
    def decode_(s):
        try:
            return s.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return s.decode('gb18030')
            except UnicodeDecodeError:
                return s.decode('utf-8', 'replace')

    def get_message(self):
        if self.content_type == 2:
            return self._eml()
        else:
            return self._html()

    def _eml(self):
        try:
            content = MulTemplateEmail.encode_(self.content)
        except:
            content = MulTemplateEmail.decode_(self.content)
        self.message = email.message_from_string(content)
        return self.message.as_string()

    # 生成一个长度为n的数字串
    def _make_rand_nums(self, n=10):
        # noinspection PyUnusedLocal
        return "".join([str(random.randint(0, 9)) for i in range(n)])

    # 生成 Message-Id
    def _makeMsgId(self):
        msgid_stat = random.randint(1,10000)
        user_id = random.randint(1,10000)
        msgid_domain = self.mail_from.split('@')[-1]
        task_ident = '{}-{}-{}'.format(time.strftime('%Y%m%d%H%M%S'), user_id, random.randint(10, 100))
        mid = "<%s.{RANDOM}-{%s:%s}-{COUNT}@{DOMAIN}>" % (time.strftime("%Y%m%d%H%M%S"), user_id, task_ident)
        mid = mid.replace('{COUNT}', "%07d" % msgid_stat)
        mid = mid.replace('{RANDOM}', self._make_rand_nums(5))
        mid = mid.replace('{DOMAIN}', msgid_domain)
        return mid

    def _html(self):
        """
        # 发送一个包含纯文本、html和附件邮件：
        # 发送成功少纯文本的内容，代码没有报错，把其他的代码注掉仅发送纯文本内容，纯文本中的内容在邮件中是能看到的。
        """
        # mul Header
        # self.message['Content-Transfer-Encoding'] = self.encoding
        # self.message.replace_header('Content-Transfer-Encoding', self.encoding)
        self.message['Message-Id'] = Header(self._makeMsgId(), self.character)
        if self.reply_to:
            self.message['Reply-to'] = Header(self.reply_to, self.character)
        self.message['Subject'] = Header(self.subject, self.character)
        self.message['From'] = Header(self.mail_from, self.character)
        self.message['To'] = Header(self.mail_to, self.character)
        self.message["Date"] = formatdate(localtime=True)
        if self.is_need_receipt:
            self.message['Disposition-Notification-To'] = Header(self.mail_from, self.character)
            # self.message['Disposition-Notification-To'] = Header('1248644045@qq.com')
        if self.edm_check_result:
            self.message['Edm-Check-Result'] = Header(self.edm_check_result, self.character)


        # mul Content(html或纯文本)
        if self.text_content:
            if self.encoding == "base64":
                mt = MIMEText(self.text_content, 'plain', self.character)
            else:
                mt = MIMEText(None, _subtype="plain")
                mt.replace_header('content-transfer-encoding', self.encoding)
                mt.set_payload(self.text_content.encode(self.character).encode('quoted-printable'), self.character)
            self.message.attach(mt)
        if self.content:
            if self.encoding == "base64":
                mt = MIMEText(self.content, 'html', self.character)
            else:
                mt = MIMEText(None, _subtype="html")
                mt.replace_header('content-transfer-encoding', self.encoding)
                mt.set_payload(self.content.encode(self.character).encode('quoted-printable'), self.character)

            self.message.attach(mt)
        # self.message.attach(self.msgAlternative)

        # mul Attachment(附件，传统附件解析)
        for filepath, filetype, filename in self.attachment:
            try:
                real_filepath = os.path.join(self.attachment_path, str(self.template_id), filepath.encode('utf-8'))
                attachment = MIMEText(open(real_filepath, 'r').read(), self.encoding, self.character)
                attachment['Content-Type'] = filetype
                attachment['Content-Disposition'] = 'attachment;filename="%s"' % Header(filename, self.character)
                self.message.attach(attachment)
            except BaseException as e:
                print e
                continue

        return self.message.as_string()
