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

from apps.core.models import Customer, Cluster, IpPool
from lib.django_redis import get_redis as get_redis_connection
from django.core.cache import cache
from lib.common import get_auth_key
from django.utils.translation import ugettext_lazy as _
from auditlog.registry import auditlog


MAIL_STATE = (
    ('', '--'),
    ('check', u'等待检测'),
    ('review', u'等待审核'),
    ('dispatch', u'等待分配IP'),
    ('send', u'等待发送'),
    ('reject', u'拒绝'),
    ('c_reject', u'客户拒绝'),
    ('retry', u'等待重试'),
    ('bounce', u'等待退信'),
    ('finished', u'出站成功'),
    ('fail_finished', u'出站失败'),
)

STATE_RELATE = {
    'check': 'analysis',
    'review': 'analysis',
    # 'dispatch': 'analysis',
    'bounce': 'fail_finished',
}

STATE_RELATE2 = (
    ('', _(u'--')),
    ('check', _(u'疑似垃圾邮件,深度分析中...')),
    ('review', _(u'疑似垃圾邮件,深度分析中...')),
    ('dispatch', _(u'通道传输中')),
    ('send', _(u'正在出站')),
    ('reject', _(u'系统已过滤')),
    ('c_reject', _(u'我已过滤')),
    ('retry', _(u'重试出站')),
    ('bounce', _(u'出站失败')),
    ('fail_finished', _(u'出站失败')),
    ('finished', _(u'出站成功'))
)

DSPAM_STUDY = (
    ('', '--'),
    (0, u'无学习'),
    (1, u'垃圾邮件'),
    (2, u'正常邮件'),
)

CHECK_RESULT = (
    ('', _(u'--')),
    ('error_format', _(u'格式错误')),
    ('invalid_mail', _(u'无效地址')),
    ('recipient_blacklist', _(u'收件人黑名单')),
    ('recipient_whitelist', _(u'收件人白名单')),
    ('domain_blacklist', _(u'域名黑名单')),
    ('active_spam', _(u'动态SPAM')),
    ('high_risk', _(u'高危邮件')),
    ('sender_blacklist', _(u'发件黑')),
    ('keyword_blacklist', _(u'内容黑')),
    ('subject_blacklist', _(u'主题黑')),
    ('custom_blacklist', _(u'自动回复')),
    ('subject_and_keyword', _(u'主题和内容关键字')),
    ('bulk_email', _(u'群发邮件')),
    ('bulk_email_subject', _(u'群发邮件(主题)')),
    ('big_email', _(u'大邮件')),
    ('innocent', _(u'正常邮件')),
    ('spam', _(u'垃圾邮件(dspam)')),
    ('cyber_spam', _(u'CYBER-Spam')),
    ('spamassassin', _(u'垃圾邮件(spamassassin)')),
    ('virus', _(u'病毒')),
    ('auto_reject', _(u'自动审核-拒绝')),
    ('k_auto_reject', _(u'关键字免审-拒绝')),
    ('auto_pass', _(u'自动审核-通过')),
    ('error', _(u'检测出错')),
    ('auto_reject_attach', _(u'自动拒绝-小危附件')),
    ('esets', _(u'Esets 病毒')),
    ('sender_whitelist', _(u'发件人白名单')),
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
    ('ip', u'IP'),
    ('ip_pool', u'IP池'),
    ('cluster', u'SMTP发送机'),
    ('customer', u'客户'),
)

ERROR_TYPE = (
    ('', u'--'),
    (0, u'无'),
    (1, u'连接错误-1'),
    (2, u'邮箱不存在'),
    (3, u'其他错误'),
    (4, u'超大/满'),
    (5, u'垃圾邮件'),
    (6, u'不重试邮件'),
    (7, u'spf邮件'),
    (8, u'发送超时'),
)

ERROR_TYPE_DISPLAY = {
    1: u'连接异常。',
    2: u'收件人地址不存在或无效邮箱。',
    4: u'邮件超大或邮箱空间满。',
    5: u'垃圾邮件。',
    7: u'spf错误。',
    8: u'连接超时。'
}

RETRY_MODE = (
    ('single_ip', u'单IP轮询'),
    ('multi_ip', u'多IP轮询'),
)

MAIL_FLOW = {
    'review': ('check', ),
    'reject': ('check', 'review'),
    'dispatch': ('check', 'review'),
    'send': ('dispatch', ),
    'retry': ('send', ),
    'bounce': ('send', 'retry'),
    'finished': ('send', 'retry', 'bounce'),
}

CUSTOM_KEYWORD_BLACKLIST_TYPE = (
    ('subject', u'主题'),
    ('content', u'内容'),
)

BULKCUSTOMER_STATUS = (
    ('deal', u'待处理'),
    ('dealed', u'已处理'),
)

CUSTOMER_REPORT = (
    (0, u'无'),
    (1, u'已举报'),
    (2, u'已处理(通过)'),
    (-1, u'已处理(拒绝)')
)

MAIL_SERVERS = (
    ('shenzhen', _(u'深圳')),
    ('hangzhou', _(u'杭州')),
)


def get_mail_model(db_table):
    class CustomMetaClass(models.base.ModelBase):
        def __new__(cls, name, bases, attrs):
            model = super(CustomMetaClass, cls).__new__(cls, name, bases, attrs)
            model._meta.db_table = 'mail_{}'.format(db_table)
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
        dispatch_data = models.TextField(u'dispatch_data', null=True, blank=True)
        deliver_time = models.DateTimeField(u'发送时间', null=True, blank=True)
        deliver_ip = models.GenericIPAddressField(u'发送IP', null=True, blank=True)
        return_code = models.SmallIntegerField(null=True, blank=True)
        return_message = models.TextField()
        mail_from = models.CharField(u'发件人', max_length=150, null=True, blank=True)
        sender_name = models.CharField(u'发件人姓名', max_length=100, null=True, blank=True)
        mail_to = models.CharField(u'收件人', max_length=150, null=True, blank=True)
        subject = models.CharField(u'主题', max_length=800, null=True, blank=True)
        client_ip = models.GenericIPAddressField(u'客户端IP', null=True, blank=True)
        # state = StateField(machine=MailStateMachine, default='check', choices=MAIL_STATE, db_index=True)
        state = models.CharField(u'状态', max_length=20, default='check', choices=STATE_RELATE2, db_index=True)
        dspam_sig = models.CharField(u'dspam的signature', max_length=50, null=True, blank=True)
        bounce_result = models.CharField(u'退信结果', choices=FAIL_OR_SUCCESS, max_length=20, null=True, blank=True)
        bounce_time = models.DateTimeField(u'退信时间', null=True, blank=True)
        bounce_message = models.TextField()
        size = models.IntegerField(u'邮件大小', default=0)
        error_type = models.IntegerField(u'发送错误类型', default=0, choices=ERROR_TYPE)
        dspam_study = models.SmallIntegerField(u'dspam学习结果', choices=DSPAM_STUDY, default=0)
        customer_report = models.SmallIntegerField(u'客户垃圾举报', choices=CUSTOMER_REPORT, default=0)
        server_id = models.CharField(u'所在服务器的ID', max_length=20, default='shenzhen', choices=MAIL_SERVERS,
                                     db_index=True)

        def get_mail_content(self):
            file_path = self.get_mail_path()
            file_path_old = self.get_mail_path_old()

            if os.path.exists(file_path):
                return open(file_path, 'r').read()

            if os.path.exists(file_path_old):
                return open(file_path_old, 'r').read()

            # 判断是否需要从其他服务器同步邮件内容
            if self.server_id != settings.SERVER_ID and self.size < get_sync_max_size():
                server = self.server_id.upper()
                url = 'http://{}/mail/send_mail_file?id={}&auth={}'.format(getattr(settings, 'WEB_{}'.format(server)),
                                                                           self.date_id(), get_auth_key())
                with open(file_path, 'w') as fw:
                    content = urllib2.urlopen(url).read()
                    fw.write(content)
                return content
            return ''

        def is_exists(self):
            return os.path.exists(self.get_mail_path())

        def get_mail_path(self):
            # file_name = '{},{},{},{},{}'.format(self.id, self.customer_id, self.mail_from, self.mail_to)
            file_name = self.get_mail_filename()
            return os.path.join(settings.DATA_PATH, db_table, file_name)
            # return os.path.realpath(os.path.join(os.path.dirname(__file__), '../../../data', db_table, file_name))

        def get_mail_path_old(self):
            file_name = '{},{},{},{},{}'.format(db_table, self.id, self.customer_id, self.mail_from,
                                                self.mail_to).replace('/', '')
            return os.path.join(settings.DATA_PATH, db_table, file_name)

        def get_mail_filename(self):
            return '{},{}'.format(db_table, self.id)

        def get_mail_size(self):
            return len(self.get_mail_content())

        def get_mail_id(self):
            """
            获取是同一封邮件的ID
            :return:
            """
            return self.mail_id if self.mail_id else self.id

        def save_mail_for_pop(self):
            """
            将邮件内容存入归档邮箱
            :return:
            """
            max_size = get_max_size()
            if max_size and self.size >= max_size:
                return
            try:
                shutil.copy(self.get_mail_path(), settings.MAIL_LOCATION)
            except Exception, e:
                pass

        def save(self, *args, **kwargs):
            """
            根据状态判断是否保存, 保存状态改变记录
            :param args:
            :param kwargs:
            :return:
            """
            try:
                new_state = getattr(self, 'state')
                self.refresh_from_db(fields=('state', ))
                old_state = getattr(self, 'state')
                if new_state != old_state:
                    MailStateLog.objects.create(date=self.get_date(), mail_id=self.id, new_state=new_state,
                                                old_state=old_state)
                setattr(self, 'state', new_state)
            except:
                pass
            super(Mail, self).save(*args, **kwargs)

            # 邮件大小超过某个阀值的 发送完成后 直接删除
            max_size = get_max_size()
            if new_state == 'finished' and max_size and self.size >= max_size:
                self.clear_mail()


        def get_date(self):
            return self._meta.db_table.split('_')[1]


        def date_id(self):
            return '{}_{}'.format(self.get_date(), self.id)

        def _do_error_type(self):
            """
            根据错误类型进行相应操作，
            在日志回传保存的 server.py中调用
            :return:
            """
            # 保存无效地址
            redis = get_redis_connection()
            if self.error_type == 2:
                InvalidMail.objects.get_or_create(mail=self.mail_to.lower())

            # 垃圾邮件发送者 加入动态spam检测队列
            if self.error_type == 5:
                redis_key = 'relay_spam_sender_history'
                mail_from = self.mail_from.lower()
                s = redis.hget(redis_key, mail_from)
                if s:
                    s = '{},{}'.format(int(time.time()), s)
                else:
                    s = str(int(time.time()))
                redis.hset(redis_key, mail_from, s)
                redis.hset(redis_key, 'is_need_update', 'True')
                # if not redis.hexists(redis_key, mail_from):
                # redis.hset('relay_spam_sender', mail_from, time.time())

            # spf错误域名 保存到SpfError
            if self.error_type == 7:
                domain = self.mail_from.split('@')[-1]
                SpfError.objects.get_or_create(domain=domain, customer=self.customer)


        def get_retry_count(self):
            return DeliverLog.objects.filter(date=self.get_date(), mail_id=self.id).count()


        def clear_mail(self):
            file_path = self.get_mail_path()
            if os.path.exists(file_path):
                os.unlink(file_path)

        def return_message_display(self):
            return u'{}{}'.format(ERROR_TYPE_DISPLAY.get(self.error_type, ''), self.return_message)

        def can_undo(self):
            """客户每天误判操作不能超过100次"""
            key = 'customer_pass_undo'
            redis = get_redis_connection()
            try:
                undo_count = int(redis.hget(key, self.customer.id))
            except:
                undo_count = 0
            return undo_count < 100

    return Mail


def get_max_size():
    cache_key = '_cache:max_size'
    max_size = cache.get(cache_key)
    if max_size is None:
        objs = Settings.objects.all()
        max_size = objs[0].max_size * 1024 if objs else 0
        cache.set(cache_key, max_size, 600)
    return max_size


def get_sync_max_size():
    cache_key = '_cache:sync_max_size'
    max_size = cache.get(cache_key)
    if max_size is None:
        objs = Settings.objects.all()
        max_size = objs[0].sync_max_size * 1024 if objs else 0
        cache.set(cache_key, max_size, 600)
    return max_size


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


class DomainBlacklist(models.Model):
    domain = models.CharField(u'域名关键字', max_length=50, null=False, blank=False,
                              help_text=u"发件人如果包含某些域名，比如qq.com 163.com，这样的邮件接收后删除，支持通配符录入黑名单数据，例如.*\.yahoo\..* (这个代表*.yahoo.com   *.yahoo.com.cn   *.yahoo.jp等) ")
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    hits = models.IntegerField(u'命中次数', default=0)

    def __unicode__(self):
        return self.domain


class SubjectKeywordBlacklist(models.Model):
    keyword = models.CharField(u'主题关键字', max_length=50, null=False, blank=False,
                               help_text=u"邮件主题如果含有黑名单关键词，则将该邮件挂起并交给管理员审核,支持通配符?，例如“发.{1}票”或“发.{2}票”，这样，则“发a票” 或 “发aa票”")
    direct_reject = models.BooleanField(u'是否不用审核，直接拒绝', default=False)
    relay = models.BooleanField(u'是否用于中继', default=True)
    collect = models.BooleanField(u'是否用于代收', default=True)
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    def __unicode__(self):
        return self.keyword


class KeywordBlacklist(models.Model):
    keyword = models.CharField(u'内容关键字', max_length=50, null=False, blank=False,
                               help_text=u"邮件内容如果含有黑名单关键词，则将该邮件挂起并交给管理员审核,支持通配符?，例如“发.{1}票”或“发.{2}票”，这样，则“发a票” 或 “发aa票”")
    direct_reject = models.BooleanField(u'是否不用审核，直接拒绝', default=False)
    relay = models.BooleanField(u'是否用于中继', default=True)
    collect = models.BooleanField(u'是否用于代收', default=True)
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    def __unicode__(self):
        return self.keyword


class CheckSettings(models.Model):
    bulk_max = models.IntegerField(u'群发邮件阀值', null=False, blank=False, default=10,
                                   help_text=u"24小时内,相同主题的邮件超过该值,则被认为是群发邮件")
    bulk_expire = models.IntegerField(u'群发邮件过期天数', null=False, blank=False, default=7,
                                      help_text=u"单位:天数, 如果邮件被认为是群发邮件, 则相应天数里,相同主题将被检测")
    max_size = models.IntegerField(u'邮件最大值', null=False, blank=False, default=50,
                                   help_text=u"单位:M, 能够接收的邮件最大值, 默认50M")
    spam_score_max = models.FloatField(u'spam检测分数阀值(白天)', null=False, blank=False, default=5.0,
                                       help_text=u'白天(07:00--19:00)如果spam检测分数超过该阀值, 则被认为是垃圾邮件, 默认为5.0')
    night_spam_score_max = models.FloatField(u'spam检测分数阀值(晚上)', null=False, blank=False, default=4.0,
                                             help_text=u'晚上(19:00--07:00)如果spam检测分数超过该阀值, 则被认为是垃圾邮件, 默认为5.0')
    sender_max_size = models.IntegerField(u'发件人检测阀值', null=False, blank=False, default=0,
                                          help_text=u"单位:KB, 邮件如果超过该阀值, 则直接放行, 不进行检测, 默认0KB, 表示全部检测")
    subject_max_size = models.IntegerField(u'主题检测阀值', null=False, blank=False, default=0,
                                           help_text=u"单位:KB, 邮件如果超过该阀值, 则直接放行, 不进行检测, 默认0KB, 表示全部检测")
    content_max_size = models.IntegerField(u'内容检测阀值', null=False, blank=False, default=0,
                                           help_text=u"单位:KB, 邮件如果超过该阀值, 则直接放行, 不进行检测, 默认0KB, 表示全部检测")
    spam_max_size = models.IntegerField(u'Spamassassin检测阀值', null=False, blank=False, default=0,
                                        help_text=u"单位:KB, 邮件如果超过该阀值, 则直接放行, 不进行检测, 默认0KB, 表示全部检测")
    dspam_max_size = models.IntegerField(u'Dspam检测阀值', null=False, blank=False, default=0,
                                         help_text=u"单位:KB, 邮件如果超过该阀值, 则直接放行, 不进行检测, 默认0KB, 表示全部检测")
    ctasd_max_size = models.IntegerField(u'Ctasd检测阀值', null=False, blank=False, default=0,
                                         help_text=u"单位:KB, 邮件如果超过该阀值, 则直接放行, 不进行检测, 默认0KB, 表示全部检测")
    custom_max_size = models.IntegerField(u'自动回复检测阀值', null=False, blank=False, default=0,
                                          help_text=u"单位:KB, 邮件如果超过该阀值, 则直接放行, 不进行检测, 默认0KB, 表示全部检测")
    attachment_min_size = models.IntegerField(u'小危附件阀值', null=False, blank=False, default=0,
                                              help_text=u"单位:KB, 邮件附件是rar或zip类型，且大小小于该阀值, 则认为是高危邮件, 默认0KB, 表示不检测")
    active_spam_monitor_time = models.IntegerField(u'动态邮件(监测时间monitor_time)', null=False, blank=False, default=60,
                                                   help_text=u"单位:分钟, 某个发件人在(monitor_time)分钟内出现(max)次垃圾邮件特征后(check_time)小时内的邮件进行审核")
    active_spam_max = models.IntegerField(u'动态邮件(数量阀值max)', null=False, blank=False, default=1,
                                          help_text=u"单位:邮件封数, 某个发件人在(monitor_time)分钟内出现(max)次垃圾邮件特征后(check_time)小时内的邮件进行审核")
    active_spam_check_time = models.IntegerField(u'动态邮件(检测时间check_time)', null=False, blank=False, default=24,
                                                 help_text=u"单位:小时, 某个发件人在(monitor_time)分钟内出现(max)次垃圾邮件特征后(check_time)小时内的邮件进行审核")
    bulk_sender_time = models.IntegerField(u'群发单个发件人监测时间', null=False, blank=False, default=10,
                                           help_text=u'单位：分钟，群发监测单个发件人的时间')
    bulk_sender_max = models.IntegerField(u'群发单发件人发送阀值', null=False, blank=False, default=10,
                                          help_text=u'单个发件人在监测时间内允许发的邮件封数，超过的接收并丢弃，将邮件数计入群发')
    auto_review_time = models.IntegerField(u'自动审核对应关系监测时间', null=False, blank=False, default=3,
                                           help_text=u'单位：天数, 自动审核中，监测发件人-收件人对应关系的时间')
    auto_review_num = models.IntegerField(u'自动审核操作次数', null=False, blank=False, default=10,
                                          help_text=u'单位：操作次数, 自动审核中，发件人-收件人连续X次通过/拒绝,则记录相应关系')
    auto_review_expire = models.IntegerField(u'自动审核对应关系过期时间', null=False, blank=False, default=365,
                                             help_text=u'单位：天数, 自动审核中，发件人-收件人对应关系过期时间')
    auto_review_time_start = models.IntegerField(u'自动审核有效开始时间', null=False, blank=False, default=7,
                                                 help_text=u'0-24之内的整数，默认早上7点，自动审核开始工作时间， 只有在早上X点到晚X点 自动审核才工作')
    auto_review_time_end = models.IntegerField(u'自动审核有效结束时间', null=False, blank=False, default=19,
                                               help_text=u'0-24之内的整数，默认晚上19点，自动审核开始工作时间， 只有在早上X点到晚X点 自动审核才工作')


class BounceSettings(models.Model):
    server = models.CharField(u'SMTP服务器', max_length=50, null=False, blank=False)
    port = models.IntegerField(u'端口', default=25)
    is_ssl = models.BooleanField(u'SSL加密', default=False)
    mailbox = models.CharField(u'邮箱帐号', max_length=50, null=False, blank=False)
    password = models.CharField(u'邮箱密码', max_length=50, null=False, blank=False)
    template_cn = models.TextField(u'中文模板', help_text=u'支持变量: {reason}表示退信原因, {origin}表示不含附件的原始邮件')
    template_en = models.TextField(u'英文模板', help_text=u'支持变量: {reason}表示退信原因, {origin}表示不含附件的原始邮件')


class SubjectKeywordWhitelist(models.Model):
    keyword = models.CharField(u'主题关键字', max_length=50, null=False, blank=False,
                               help_text=u"邮件主题如果含有白名单关键词，则将该邮件不会进行群发邮件检测,支持通配符?，例如“发.{1}票”或“发.{2}票”，这样，则“发a票” 或 “发aa票”")
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    def __unicode__(self):
        return self.keyword


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
    ip = models.CharField(u'IP', null=True, blank=True, max_length=20)
    ip_pool = models.ForeignKey(IpPool, null=True, blank=True, on_delete=models.SET_NULL)
    cluster = models.ForeignKey(Cluster, null=True, blank=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING,
                                 related_name='relay_statistics')

    def __unicode__(self):
        return self.date


class SenderBlacklist(models.Model):
    keyword = models.CharField(u'关键字', max_length=50, null=False, blank=False,
                               help_text=u"收件人如果含有黑名单关键词，则将该邮件挂起,交给管理员审核,支持正则表达式")
    direct_reject = models.BooleanField(u'是否不用审核，直接拒绝', default=False)
    relay = models.BooleanField(u'是否用于中继', default=True)
    collect = models.BooleanField(u'是否用于代收', default=True)
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    def __unicode__(self):
        return self.keyword


class InvalidMail(models.Model):
    mail = models.CharField(u'邮件地址', max_length=150, null=False, blank=False, unique=True, db_index=True,
                            help_text=u"无效邮件地址")
    # disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    def __unicode__(self):
        return self.mail


class DeliverLog(models.Model):
    date = models.CharField(u'日期', max_length=20)
    mail_id = models.IntegerField()
    deliver_ip = models.GenericIPAddressField(u'发送IP', null=True, blank=True)
    deliver_time = models.DateTimeField(u'发送时间', null=True, blank=True)
    mx_record = models.CharField(u'mx 记录', max_length=200, null=True, blank=True)
    receive_ip = models.GenericIPAddressField(u'接收IP', null=True, blank=True)
    return_code = models.SmallIntegerField(null=True, blank=True)
    return_message = models.TextField()

    class Meta:
        index_together = [
            ['date', 'mail_id'],
        ]


class RecipientBlacklist(models.Model):
    keyword = models.CharField(u'关键字', max_length=50, null=False, blank=False,
                               help_text=u"收件人如果含有黑名单关键词，则将该邮件当无效收件地址处理, 支持正则表达式")
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    def __unicode__(self):
        return self.keyword


class Settings(models.Model):
    retry_mode = models.CharField(u'重试方式', max_length=20, default='single_ip', choices=RETRY_MODE)
    back_days = models.IntegerField(u'邮件备份日期', default=30, help_text=u'单位：天数，超过该天数的原始邮件将会被自动清除')
    expired_days = models.IntegerField(u'客户过期延长天数', default=15, help_text=u'单位：天数，如果客户服务到期，可延长发送相应天数')
    bulk_customer = models.IntegerField(u'群发客户阀值', default=1000, help_text=u'每天“群发+DSPAM+格错+收黑” 数超过X的客户标志为群发客户')
    max_size = models.IntegerField(u'大邮件阀值', default=0, help_text=u'单位：KB，如果邮件大小超过该阀值，则该邮件不加入归档邮箱写发成功后直接删除，0表示该设置无效')
    sync_max_size = models.IntegerField(u'邮件同步最大阀值', default=800, help_text=u'单位：KB，如果邮件大小超过该阀值，则该邮件内容不会同步到其他服务器')
    big_email = models.IntegerField(u'传输大邮件阀值', default=20, help_text=u'单位：MB，大于XXX kb的邮件从大邮件地址池发，如果发送失败，再从之前的通道发')
    big_email_pool = models.ForeignKey(IpPool, null=True, blank=True, on_delete=models.SET_NULL, help_text=u'大邮件发送池',
                                       verbose_name=u'大邮件发送池')


class SpfError(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True, blank=True)
    domain = models.CharField(u'域名关键字', max_length=200, null=False, blank=False, help_text=u"spf错误域名")
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    status = models.CharField(u'状态', max_length=10, choices=BULKCUSTOMER_STATUS, default='deal')

    def __unicode__(self):
        return self.domain


class CustomKeywordBlacklist(models.Model):
    keyword = models.CharField(u'自动回复关键字', max_length=50, null=False, blank=False,
                               help_text=u"邮件内容或主题如果含有黑名单关键词，则将该邮件挂起并交给管理员审核,支持通配符?，例如“发.{1}票”或“发.{2}票”，这样，则“发a票” 或 “发aa票”")
    type = models.CharField(u'检测类型', max_length=10, choices=CUSTOM_KEYWORD_BLACKLIST_TYPE, default='subject')
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    def __unicode__(self):
        return self.keyword


class ValidMailSuffix(models.Model):
    keyword = models.CharField(u'邮件后缀名', max_length=50, null=False, blank=False,
                               help_text=u"有效的邮件后缀名")
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    def __unicode__(self):
        return self.keyword


class AttachmentBlacklist(models.Model):
    """
    附件黑名单
    """
    keyword = models.CharField(u'附件关键字', max_length=50, null=False, blank=False,
                               help_text=u"对附件进行检测，如果附件名称包含黑名单关键词,　则将邮件标志为高危邮件审核。支持正则")
    relay = models.BooleanField(u'是否用于中继', default=True)
    collect = models.BooleanField(u'是否用于代收', default=True)
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    def __unicode__(self):
        return self.keyword


class MailStateLog(models.Model):
    date = models.CharField(u'日期', max_length=20)
    mail_id = models.IntegerField()
    old_state = models.CharField(u'旧状态', max_length=20, default='check', choices=MAIL_STATE)
    new_state = models.CharField(u'新状态', max_length=20, default='check', choices=MAIL_STATE)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    class Meta:
        index_together = [
            ['date', 'mail_id'],
        ]


class BulkCustomer(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True, blank=True)
    date = models.DateField()
    spam_count = models.IntegerField(u'垃圾邮件数', default=0)
    sender = models.TextField(u'垃圾邮件数')
    sender_count = models.IntegerField(u'垃圾邮件数', default=0)
    recent_count = models.IntegerField(u'最近发送次数', default=0)
    status = models.CharField(u'状态', max_length=10, choices=BULKCUSTOMER_STATUS, default='deal')


class SenderWhitelist(models.Model):
    sender = models.CharField(_(u'发件人'), max_length=150, null=False, blank=False,
                              help_text=_(
                                  u"发件人白名单 如果发件人在白名单中，跳过后面所有的网关检测, 不支持正则标准,支持整域名过滤，如test.com且下面选中为域名，表示整个test.com为域名的发件人为白名单发件人"))
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True, blank=True)
    is_domain = models.BooleanField(_(u'是否为域名'), default=False, help_text=_(u'当选中时，整个域名都为白名单，默认不选中'))
    is_global = models.BooleanField(_(u'是否为全局变量'), default=False, help_text=_(u'全局白，是对所有客户生效。客户白，仅仅对这个客户生效'))
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    disabled = models.BooleanField(_(u'是否禁用'), default=False)
    created = models.DateTimeField(_(u'创建日期'), auto_now_add=True)

    def __unicode__(self):
        return self.sender


class CustomerSenderBlacklist(models.Model):
    """ 用户发件人黑名单 """
    sender = models.CharField(_(u'发件人'), max_length=150, null=False, blank=False,
                              help_text=_(
                                  u'发件人黑名单：如果发件人在黑名单中，则不进行网关检测直接拒绝, 不支持正则标准,支持整域名过滤，如test.com且下面选中为域名，表示整个test.com为域名的发件人为黑名单发件人'))
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING)
    is_domain = models.BooleanField(_(u'是否为域名'), default=False, help_text=_(u'当选中时，整个域名都为黑名单，默认不选中'))
    is_global = models.BooleanField(_(u'是否为全局变量'), default=False, help_text=_(u'全局黑，是对所有客户生效。客户黑，仅仅对这个客户生效'))
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    disabled = models.BooleanField(_(u'是否禁用'), default=False)
    created = models.DateTimeField(_(u'创建日期'), auto_now_add=True)

    def __unicode__(self):
        return self.sender


class InvalidSenderWhitelist(models.Model):
    sender = models.CharField(u'发件人', max_length=150, null=False, blank=False,
                              help_text=u"无效地址发件人白名单 如果发件人在白名单中，跳过中继无效地址检测")
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    def __unicode__(self):
        return self.sender


class CollectRecipientWhitelist(models.Model):
    keyword = models.CharField(_(u'收件人'), max_length=50, null=False, blank=False, unique=True,
                               help_text=_(u"网关收件人白名单, 如果收件人在白名单中，网关对该发件人不做任何过滤"))
    disabled = models.BooleanField(_(u'是否禁用'), default=False)
    created = models.DateTimeField(_(u'创建日期'), auto_now_add=True)
    operate_time = models.DateTimeField(_(u'最后操作日期'), null=True, auto_now=True)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING)

    def __unicode__(self):
        return self.keyword


class SpamRptBlacklist(models.Model):
    """ 网关隔离报告黑名单 """
    recipient = models.CharField(u'收件人', max_length=150, null=False, blank=False,
                                 help_text=u'隔离报告收件人黑名单:如果收件人在黑名单中，则隔离报告不发送给该发件人')
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING)
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.recipient

auditlog.register(SenderWhitelist, include_fields=['sender', 'customer', 'is_regex', 'is_domain', 'disabled'])
auditlog.register(CustomerSenderBlacklist, include_fields=['sender', 'customer', 'is_regex', 'is_domain', 'disabled'])
auditlog.register(InvalidSenderWhitelist, include_fields=['sender', 'disabled'])
auditlog.register(CollectRecipientWhitelist, include_fields=['keyword', 'disabled'])
auditlog.register(SpamRptBlacklist, include_fields=['recipient', 'customer', 'disabled'])
