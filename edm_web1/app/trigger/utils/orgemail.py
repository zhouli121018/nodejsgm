# -*- coding: utf-8 -*-

import os
import re
import urllib
import string
import time, email, base64, quopri, random
from email.utils import formatdate
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMENonMultipart import MIMENonMultipart
from django.conf import settings
from email.header import Header, decode_header, make_header
from lib.tools import safe_format
from app.trigger.utils.const import CNCHARS

CHARS = string.lowercase + string.digits

#############################################
### 通过邮件模板构造一个可以发送html、纯文本、附件的邮件 ###
class OrgMessage(object):
    def __init__(self, content_type=1, character='utf-8', encoding='base64',
                 user_id=None,  template_id=None,
                 subject='', content='', text_content=None, edm_check_result=None,
                 attachment=None, send_name=None,
                 task_id=None, send_maillist_id=None, task_ident=None,
                 mail_from=u'system@bestedm.org', mail_to=u'test@bestedm.org', reply_to=None,
                 is_need_receipt=False, track_domain=None):
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
        self.user_id=user_id
        self.template_id = template_id
        self.task_ident = task_ident
        # self.mail_from = mail_from
        # self.send_name = send_name
        self.__makeEncodeAddr(mail_from, send_name)
        self.mail_to = mail_to
        self.reply_to = reply_to
        self.edm_check_result = edm_check_result
        self.is_need_receipt = is_need_receipt
        self.track_domain = track_domain

        self.__comkwargs(mail_from, user_id,  template_id, task_id, send_maillist_id)
        self.subject = safe_format(subject or "", **self.kwargs)
        content = content or ""
        content = content.replace("\r\n", "\n")
        self.content = safe_format(content, **self.kwargs)
        self.content = self.__addOpenlink(self.content)
        self.content = self.__addTrackLink(self.content)
        if not text_content:
            text_content = u'''如果邮件内容无法正常显示请以超文本格式显示HTML邮件！\n
            （If the content of the message does not display properly, please display the HTML message in hypertext format!）'''
        self.text_content = text_content
        self.attachment = attachment or []
        self.attachment_path = settings.ATTACH_DATA_PATH
        # self.msgAlternative = MIMEMultipart('alternative')
        self.message = MIMEMultipart('alternative')

    # 生成编码后的邮件地址
    def __makeEncodeAddr(self, mail_from, name):
        if name:
            name = name.decode('utf-8')
            en_name = str(make_header([(name, self.character)]))
        else:
            en_name = None
        self.mail_from = email.utils.formataddr((en_name, mail_from))
        self.msgid_domain = mail_from.split('@')[1]

    # 公共变量汇总
    def __comkwargs(self, mail_from, user_id=None,  template_id=None, task_id=None, send_maillist_id=None):
        self.kwargs = {}
        random_html = '''<div style="display:none;">{DATA}</div>'''.replace('{DATA}', self.__makeRandCNchars())
        self.kwargs.update(
            FULLNAME='', RECIPIENTS=self.mail_to, DATE=time.strftime("%Y-%m-%d %H:%M:%S"), RANDOM_NUMBER=self.__makeRandNums(),
            RANDOM_HTML=random_html, SENDER=mail_from,
            SEX='', BIRTHDAY='', PHONE='', AREA='',
            VAR1='', VAR2='', VAR3='', VAR4='', VAR5='', VAR6='', VAR7='', VAR8='', VAR9='', VAR10='',
            JOKE='', MOTTO='', HEALTH='', SUBJECT_STRING='',
            TEMPLATE_ID=template_id or "", USER_ID=user_id or "", SEND_ID=task_id or "", MAILLIST_ID=send_maillist_id or "",
        )

    def __addFooter(self, html, footer):
        m = re.search(r'</\s*(body|html)>', html, re.IGNORECASE)
        if m is not None:
            s = m.start()
        else:
            s = len(html)
        return html[:s] + footer + html[s:]

    ## 添加打开链接
    def __addOpenlink(self, content):
        domain = '{}.{}'.format(self.__makeRandChars(), self.track_domain)
        open_img = '<img src="http://{domain}/new_track/t3/{cryp_params}.gif" border="0" width="0" height="0" />'.format(**{
            'domain': domain,
            'cryp_params': base64.urlsafe_b64encode('{}||{}'.format(self.task_ident, self.mail_to))
        })
        return self.__addFooter(content, open_img)

    ## 添加跟踪统计
    def __addTrackLink(self, content):
        def encrypt_url(matched):
            domain = '{}.{}'.format(self.__makeRandChars(), self.track_domain)
            url = matched.group(1)
            return 'href="http://{domain}/new_track/t3/{cryp_params}"'.format(**{
                'domain': domain,
                'cryp_params': base64.urlsafe_b64encode('{}||{}||{}'.format(self.task_ident, self.mail_to, url))
            })
        return re.sub('href="?\'?([^"\'>]*)', encrypt_url, content)

    # 生成一个长度为n的数字串
    def __makeRandNums(self, n=10):
        # noinspection PyUnusedLocal
        return "".join([str(random.randint(0, 9)) for i in range(n)])

    # 生成一个start-end　随机长度的字符
    def __makeRandChars(self, start=5, end=10):
        return "".join([random.choice(CHARS) for i in range(random.randint(start, end))])

    # 生成一个长度为n的中文字符串
    def __makeRandCNchars(self, n=200):
        # noinspection PyUnusedLocal
        return "".join([CNCHARS[random.randint(0, len(CNCHARS) - 1)] for i in range(n)])

    # 生成 Message-Id
    def __makeMsgId(self):
        msgid_stat = random.randint(1, 10000)
        mid = "<%s.{RANDOM}-{%s:%s}-{COUNT}@{DOMAIN}>" % (time.strftime("%Y%m%d%H%M%S"), self.user_id, self.task_ident)
        mid = mid.replace('{COUNT}', "%07d" % msgid_stat)
        mid = mid.replace('{RANDOM}', self.__makeRandNums(5))
        mid = mid.replace('{DOMAIN}', self.msgid_domain)
        return mid

    def __call__(self, *args, **kwargs):
        if self.content_type == 2:
            return self.__eml()
        else:
            return self.__html()

    def __eml(self):
        try:
            content = OrgMessage.__encode(self.content)
        except:
            content = OrgMessage.__decode(self.content)
        self.message = email.message_from_string(content)
        return self.message.as_string()

    def __html(self):
        """
        # 发送一个包含纯文本、html和附件邮件：
        # 发送成功少纯文本的内容，代码没有报错，把其他的代码注掉仅发送纯文本内容，纯文本中的内容在邮件中是能看到的。
        """
        # mul Header
        # self.message['Content-Transfer-Encoding'] = self.encoding
        # self.message.replace_header('Content-Transfer-Encoding', self.encoding)
        self.message['Message-Id'] = Header(self.__makeMsgId(), self.character)
        if self.reply_to:
            self.message['Reply-to'] = Header(self.reply_to, self.character)
        self.message['Subject'] = Header(self.subject, self.character)
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

    @staticmethod
    def __encode(s):
        try:
            return s.encode('utf-8')
        except UnicodeDecodeError:
            try:
                return s.encode('gb18030')
            except UnicodeDecodeError:
                return s.encode('utf-8', 'replace')

    @staticmethod
    def __decode(s):
        try:
            return s.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return s.decode('gb18030')
            except UnicodeDecodeError:
                return s.decode('utf-8', 'replace')
