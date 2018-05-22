# coding=utf-8
import sys
import urllib2

import os
import shutil
import time

from django.db import models
from django.core.management import color
from django.conf import settings
from django.db import connection
from apps.mail.models import get_max_size, MAIL_SERVERS, get_sync_max_size, ERROR_TYPE, ERROR_TYPE_DISPLAY
from apps.core.models import Customer
from lib.common import get_auth_key
from django.utils.translation import ugettext_lazy as _

MAIL_STATE = (
    ('', '--'),
    ('check', u'等待检测'),
    ('review', u'等待审核'),
    ('send', u'等待发送'),
    ('reject', u'拒绝'),
    ('retry', u'等待重试'),
    ('finished', u'完成'),
    ('fail_finished', u'完成(失败)'),
)

STATE_RELATE2 = (
    ('', _(u'--')),
    ('check', _(u'疑似垃圾邮件,深度分析中...')),
    ('review', _(u'疑似垃圾邮件,深度分析中...')),
    ('send', _(u'正在出站')),
    ('reject', _(u'系统已过滤')),
    ('c_reject', _(u'我已过滤')),
    ('retry', _(u'重试出站')),
    ('bounce', _(u'出站失败')),
    ('fail_finished', _(u'出站失败')),
    ('finished', _(u'出站成功'))
)

CHECK_RESULT = (
    ('', _(u'--')),
    ('spf', u'SPF错误'),
    ('error_format', _(u'格式错误')),
    ('high_risk', _(u'高危邮件')),
    ('sender_blacklist', _(u'发件黑')),
    ('keyword_blacklist', _(u'内容黑')),
    ('subject_blacklist', _(u'主题黑')),
    ('subject_and_keyword', _(u'主题和内容关键字')),
    ('innocent', _(u'正常邮件')),
    ('spam', _(u'垃圾邮件(dspam)')),
    ('cyber_spam', _(u'CYBER-Spam')),
    ('spamassassin', _(u'垃圾邮件(spamassassin)')),
    ('virus', _(u'病毒')),
    ('auto_reject', _(u'自动审核-拒绝')),
    ('error', _(u'检测出错')),
    ('sender_whitelist', _(u'发件人白名单')),
    ('c_sender_blacklist', _(u'发件人黑名单')),
)

DSPAM_STUDY = (
    ('', '--'),
    (0, u'无学习'),
    (1, u'垃圾邮件'),
    (2, u'正常邮件'),
)
REVIEW_RESULT = (
    ('', '--'),
    ('pass', u'通过'),
    ('reject', u'拒绝'),
    ('pass_undo', u'通过(误判处理)'),
    ('reject_undo', u'拒绝(误判处理)'),
    ('c_pass_undo', u'通过(客户误判处理)'),
)

FAIL_OR_SUCCESS = (
    ('', '--'),
    ('success', u'成功'),
    ('fail', u'失败')
)

STATISTICS_TYPE = (
    ('all', u'全部'),
    ('customer', u'客户'),
)

CUSTOM_KEYWORD_BLACKLIST_TYPE = (
    ('subject', u'主题'),
    ('content', u'内容'),
)
ERROR_TYPE = (
    ('', _(u'--')),
    (0, _(u'无')),
    (1, _(u'连接错误-1')),
    (2, _(u'邮箱不存在')),
    (3, _(u'其他错误')),
    (4, _(u'超大/满')),
    (5, _(u'垃圾邮件')),
    (6, _(u'不重试邮件')),
    (7, _(u'spf邮件')),
)
CUSTOMER_REPORT = (
    (0, u'无'),
    (1, u'已举报'),
    (2, u'已处理(通过)'),
    (-1, u'已处理(拒绝)')
)


def get_mail_model(db_table):
    class CustomMetaClass(models.base.ModelBase):
        def __new__(cls, name, bases, attrs):
            model = super(CustomMetaClass, cls).__new__(cls, name, bases, attrs)
            model._meta.db_table = 'cmail_{}'.format(db_table)
            return model


    class Mail(models.Model):
        __metaclass__ = CustomMetaClass

        customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True, blank=True)
        mail_id = models.IntegerField(u'关联同一封邮件的Mail ID', default=0,
                                      help_text=u'如果是默认值0, 表示是第一封邮件, 如果不是, 则和关联ID的mail是同一封邮件')
        check_result = models.CharField(u'检测结果', max_length=20, null=True, blank=True, choices=CHECK_RESULT,
                                        db_index=True)
        check_message = models.TextField(u'检测详细结果', null=True, blank=True)
        created = models.DateTimeField(u'创建日期', auto_now_add=True)
        review_result = models.CharField(u'审核结果', max_length=20, null=True, blank=True, choices=REVIEW_RESULT)
        deliver_time = models.DateTimeField(u'发送时间', null=True, blank=True)
        deliver_ip = models.GenericIPAddressField(u'发送IP', null=True, blank=True)
        return_code = models.SmallIntegerField(null=True, blank=True)
        return_message = models.TextField()
        mail_from = models.CharField(u'发件人', max_length=150, null=True, blank=True)
        sender_name = models.CharField(u'发件人姓名', max_length=50, null=True, blank=True)
        mail_to = models.CharField(u'收件人', max_length=150, null=True, blank=True)
        subject = models.CharField(u'主题', max_length=800, null=True, blank=True)
        client_ip = models.GenericIPAddressField(u'客户端IP', null=True, blank=True)
        # state = StateField(machine=MailStateMachine, default='check', choices=MAIL_STATE, db_index=True)
        state = models.CharField(u'状态', max_length=20, default='check', choices=STATE_RELATE2, db_index=True)
        dspam_sig = models.CharField(u'dspam的signature', max_length=50, null=True, blank=True)
        size = models.IntegerField(u'邮件大小', default=0)
        error_type = models.IntegerField(u'发送错误类型', default=0, choices=ERROR_TYPE)
        dspam_study = models.SmallIntegerField(u'dspam学习结果', choices=DSPAM_STUDY, default=0)
        customer_report = models.SmallIntegerField(u'客户垃圾举报', choices=CUSTOMER_REPORT, default=0)
        server_id = models.CharField(u'所在服务器的ID', max_length=20, default='shenzhen', choices=MAIL_SERVERS,
                                     db_index=True)
        bounce_result = models.CharField(u'退信结果', choices=FAIL_OR_SUCCESS, max_length=20, null=True, blank=True)
        bounce_time = models.DateTimeField(u'退信时间', null=True, blank=True)
        bounce_message = models.TextField()

        def get_mail_content(self):
            file_path = self.get_mail_path()
            file_path_old = self.get_mail_path_old()

            if os.path.exists(file_path):
                return open(file_path, 'r').read()

            if os.path.exists(file_path_old):
                return open(file_path_old, 'r').read()

            if self.server_id != settings.SERVER_ID and self.size < get_sync_max_size():
                server = self.server_id.upper()
                url = 'http://{}/collect_mail/send_mail_file?id={}&auth={}'.format(
                    getattr(settings, 'WEB_{}'.format(server)), self.date_id(), get_auth_key())
                with open(file_path, 'w') as fw:
                    content = urllib2.urlopen(url).read()
                    fw.write(content)
                return content
                # scp(self.get_mail_path(), getattr(settings, 'HOST_{}'.format(server)),
                # getattr(settings, 'PORT_{}'.format(server)))
            return ''

        def get_mail_path(self):
            file_name = self.get_mail_filename()
            return os.path.join(settings.DATA_PATH, 'c_{}'.format(db_table), file_name)


        def get_mail_path_old(self):
            file_name = '{},{},{},{},{}'.format(db_table, self.id, self.customer_id, self.mail_from,
                                                self.mail_to).replace('/', '')
            return os.path.join(settings.DATA_PATH, 'c_{}'.format(db_table), file_name)

        def get_mail_filename(self):
            return '{},{}'.format(db_table, self.id)

        def is_exists(self):
            return os.path.exists(self.get_mail_path())

        def get_mail_size(self):
            return len(self.get_mail_content())

        def get_mail_id(self):
            """
            获取是同一封邮件的ID
            :return:
            """
            return self.mail_id if self.mail_id else self.id

        def save_mail_for_pop(self):
            max_size = get_max_size()
            if max_size and self.size >= max_size:
                return
            try:
                shutil.copy(self.get_mail_path(), settings.COLLECT_MAIL_LOCATION)
            except Exception, e:
                pass

        def get_date(self):
            return self._meta.db_table.split('_')[1]


        def date_id(self):
            return '{}_{}'.format(self.get_date(), self.id)


        def get_retry_count(self):
            return DeliverLog.objects.filter(date=self.get_date(), mail_id=self.id).count()

        def clear_mail(self):
            file_path = self.get_mail_path()
            if os.path.exists(file_path):
                os.unlink(file_path)


        def save(self, *args, **kwargs):
            """
            :param args:
            :param kwargs:
            :return:
            """
            # 邮件大小超过某个阀值的 发送完成后 直接删除
            max_size = get_max_size()
            if self.state == 'finished' and max_size and self.size >= max_size:
                self.clear_mail()
            super(Mail, self).save(*args, **kwargs)

        def return_message_display(self):
            return u'{}{}'.format(ERROR_TYPE_DISPLAY.get(self.error_type, ''), self.return_message)

    return Mail


def create_mail_model(db_table):
    model = get_mail_model(db_table)
    install_model(model)
    return model


def install_model(model):
    style = color.no_style()
    output, references = connection.creation.sql_create_model(model, style)
    with connection.cursor() as cursor:
        for sql in output:
            try:
                cursor.execute(sql)
            except Exception as e:
                sys.stderr.write(
                    "Got an error recreating the test database: %s\n" % e)

    output = connection.creation.sql_indexes_for_model(model, style)
    with connection.cursor() as cursor:
        for sql in output:
            try:
                cursor.execute(sql)
            except Exception as e:
                sys.stderr.write(
                    "Got an error recreating the test database: %s\n" % e)


class SubjectKeywordBlacklist(models.Model):
    keyword = models.CharField(u'主题关键字', max_length=50, null=False, blank=False,
                               help_text=u"邮件主题如果含有黑名单关键词，则将该邮件挂起并交给管理员审核,支持通配符?，例如“发.{1}票”或“发.{2}票”，这样，则“发a票” 或 “发aa票”")
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    def __unicode__(self):
        return self.keyword


class KeywordBlacklist(models.Model):
    keyword = models.CharField(u'内容关键字', max_length=50, null=False, blank=False,
                               help_text=u"邮件内容如果含有黑名单关键词，则将该邮件挂起并交给管理员审核,支持通配符?，例如“发.{1}票”或“发.{2}票”，这样，则“发a票” 或 “发aa票”")
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    def __unicode__(self):
        return self.keyword


class CheckSettings(models.Model):
    spam_score_max = models.FloatField(u'spam检测分数阀值(白天)', null=False, blank=False, default=5.0,
                                       help_text=u'白天(07:00--19:00)如果spam检测分数超过该阀值, 则被认为是垃圾邮件, 默认为5.0')
    night_spam_score_max = models.FloatField(u'spam检测分数阀值(晚上)', null=False, blank=False, default=4.0,
                                             help_text=u'晚上(19:00--07:00)如果spam检测分数超过该阀值, 则被认为是垃圾邮件, 默认为5.0')
    subject_max_size = models.IntegerField(u'主题检测阀值', null=False, blank=False, default=0,
                                           help_text=u"单位:KB, 邮件如果超过该阀值, 则直接放行, 不进行检测, 默认0KB, 表示全部检测")
    content_max_size = models.IntegerField(u'内容检测阀值', null=False, blank=False, default=0,
                                           help_text=u"单位:KB, 邮件如果超过该阀值, 则直接放行, 不进行检测, 默认0KB, 表示全部检测")
    spam_max_size = models.IntegerField(u'Spamassassin检测阀值', null=False, blank=False, default=0,
                                        help_text=u"单位:KB, 邮件如果超过该阀值, 则直接放行, 不进行检测, 默认0KB, 表示全部检测")
    dspam_max_size = models.IntegerField(u'Dspam检测阀值', null=False, blank=False, default=0,
                                         help_text=u"单位:KB, 邮件如果超过该阀值, 则直接放行, 不进行检测, 默认0KB, 表示全部检测")
    attachment_min_size = models.IntegerField(u'小危附件阀值', null=False, blank=False, default=0,
                                              help_text=u"单位:KB, 邮件附件是rar或zip类型，且大小小于该阀值, 则认为是高危邮件, 默认0KB, 表示不检测")


class Statistics(models.Model):
    date = models.DateField(u'日期')
    type = models.CharField(u'类型', choices=STATISTICS_TYPE, max_length=20)
    count = models.IntegerField(u'总数', default=0)
    success = models.IntegerField(u'成功数', default=0)
    fail = models.IntegerField(u'失败数', default=0)
    error_type_1 = models.IntegerField(u'连接错误', default=0)
    error_type_2 = models.IntegerField(u'不存在错误', default=0)
    error_type_3 = models.IntegerField(u'其他错误', default=0)
    error_type_4 = models.IntegerField(u'超大/满的邮件', default=0)
    error_type_5 = models.IntegerField(u'垃圾邮件', default=0)
    error_type_6 = models.IntegerField(u'不重试邮件', default=0)
    error_type_7 = models.IntegerField(u'spf邮件', default=0)
    rate = models.FloatField(u'成功比', default=0)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING,
                                 related_name='collect_statistics')

    def __unicode__(self):
        return self.date


class DeliverLog(models.Model):
    date = models.CharField(u'日期', max_length=20)
    mail_id = models.IntegerField()
    deliver_ip = models.GenericIPAddressField(u'发送IP', null=True, blank=True)
    deliver_time = models.DateTimeField(u'发送时间', null=True, blank=True)
    receive_ip = models.GenericIPAddressField(u'接收IP', null=True, blank=True)
    return_code = models.SmallIntegerField(null=True, blank=True)
    return_message = models.TextField()

    class Meta:
        index_together = [
            ['date', 'mail_id'],
        ]


class Settings(models.Model):
    # retry_mode = models.CharField(u'重试方式', max_length=20, default='single_ip', choices=RETRY_MODE)
    back_days = models.IntegerField(u'邮件备份日期', default=30, help_text=u'单位：天数，超过该天数的原始邮件将会被自动清除')
    expired_days = models.IntegerField(u'客户过期延长天数', default=15, help_text=u'单位：天数，如果客户服务到期，可延长发送相应天数')


class HighRiskFlag(models.Model):
    """
    高危附件　文件类型
    """
    keyword = models.CharField(u'高危附件标志', max_length=50, null=False, blank=False,
                               help_text=u"高危附件标志, 对附件进行监控，附件的类型可定义，比如js、vbs等。含有此类附件的邮件放入高危邮件审核。")
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    def __unicode__(self):
        return self.keyword

