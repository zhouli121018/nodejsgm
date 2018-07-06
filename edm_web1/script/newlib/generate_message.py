# -*- coding: utf-8 -*-
import os
import urllib
import random
import re
import time
import email

from email.utils import formatdate
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.header import Header

from .common import safe_format, LETTERS_AND_DIGITS

ATTACH_SAVE_PATH = os.path.join('/home/umail', 'edm_data', 'attach')
TRACK_DOMAIN_DEFAULT='count.bestedm.org'

class GenerateMessage(object):
    def __init__(self, content_type=1, character='utf-8', encoding='base64',
                 template_id=0, mail_from=u'system@bestedm.org', mail_to=u'test@bestedm.org',
                 reply_to=None, task_id=None, send_maillist_id=None,
                 subject=None, content=None, text_content=None,
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
        if not encoding:  encoding='base64'
        self.character = character if character and character != 'utf8' else 'utf-8'
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
        self._relace_subject(subject, replace)
        self._relace_content(content, replace, template_id, user_id, task_id, send_maillist_id)

        if not text_content:
            text_content = u'''如果邮件内容无法正常显示请以超文本格式显示HTML邮件！\n
            （If the content of the message does not display properly, please display the HTML message in hypertext format!）'''
        self.text_content = text_content
        self.attachment = attachment
        self.attachment_path = ATTACH_SAVE_PATH
        self.message = MIMEMultipart('alternative')

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
        return "".join([random.choice(LETTERS_AND_DIGITS) for i in range(random.randint(start, end))])

    # 内容里面链接替换成客户的域名
    def _replace_href_domain(self, content):
        def encrypt_url(matched):
            domain = self.track_domain if self.track_domain else '{}.{}'.format(self._make_rand_rand_chars(), TRACK_DOMAIN_DEFAULT)
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
            domain = self.track_domain if self.track_domain else '{}.{}'.format(self._make_rand_rand_chars(), TRACK_DOMAIN_DEFAULT)
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
            content = GenerateMessage.encode_(self.content)
        except:
            content = GenerateMessage.decode_(self.content)
        self.message = email.message_from_string(content)
        return self.message.as_string()

    # 生成一个长度为n的数字串
    def _make_rand_nums(self, n=10):
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
        self.message['Message-Id'] = Header(self._makeMsgId(), self.character)
        if self.reply_to:
            self.message['Reply-to'] = Header(self.reply_to, self.character)
        try:
            self.message['Subject'] = Header(self.subject, self.character)
        except BaseException as e:
            self.message['Subject'] = Header('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', self.character)
        self.message['From'] = Header(self.mail_from, self.character)
        self.message['To'] = Header(self.mail_to, self.character)
        self.message["Date"] = formatdate(localtime=True)
        if self.is_need_receipt:
            self.message['Disposition-Notification-To'] = Header(self.mail_from, self.character)
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