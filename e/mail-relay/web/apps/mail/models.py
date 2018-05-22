# coding=utf-8
import sys
import datetime

import urllib2

import os
import shutil
import time

from django.db import models
from django.core.management import color
from django.conf import settings
from django.db import connection
from django.contrib.auth.models import User
from django.utils import timezone

from apps.core.models import Customer, Cluster, IpPool
from redis_cache import get_redis_connection as get_redis_connection2
from lib.django_redis import get_redis as get_redis_connection
from lib.common import scp
from lib.tools import get_auth_key
from django.core.cache import cache
from ordered_model.models import OrderedModel
from auditlog.registry import auditlog


MAIL_STATE = (
    ('', '--'),
    ('check', u'等待检测'),
    ('review', u'等待审核'),
    ('dispatch', u'通道传输中'),
    ('send', u'等待发送'),
    ('reject', u'拒绝'),
    ('retry', u'等待重试'),
    ('bounce', u'等待退信'),
    ('finished', u'完成'),
    ('fail_finished', u'完成(失败)'),
)

DSPAM_STUDY = (
    ('', '--'),
    (0, u'无学习'),
    (1, u'垃圾邮件'),
    (2, u'正常邮件'),
)

CHECK_RESULT = (
    ('', '--'),
    ('error_format', u'格式错误'),
    ('invalid_mail', u'无效地址'),
    ('recipient_blacklist', u'收件人黑名单'),
    ('recipient_whitelist', u'收件人白名单'),
    ('domain_blacklist', u'域名黑名单'),
    ('active_spam', u'动态SPAM'),
    ('high_risk', u'高危邮件'),
    ('high_sender', u'高危发件人'),
    ('sender_blacklist', u'发件黑'),
    ('keyword_blacklist', u'内容黑'),
    ('subject_blacklist', u'主题黑'),
    ('custom_blacklist', u'自动回复'),
    ('subject_and_keyword', u'主题和内容关键字'),
    ('bulk_email', u'群发邮件(频率)'),
    ('bulk_email_subject', u'群发邮件(主题)'),
    ('big_email', u'大邮件'),
    ('innocent', u'正常邮件'),
    ('spam', u'垃圾邮件(dspam)'),
    ('cyber_spam', u'CYBER-Spam'),
    ('spamassassin', u'垃邮(spamassassin)'),
    ('virus', u'病毒'),
    ('auto_reject', u'自动审核-拒绝'),
    ('k_auto_reject', u'关键字免审-拒绝'),
    ('auto_pass', u'自动审核-通过'),
    ('error', u'检测出错'),
    ('auto_reject_attach', u'自动拒绝-小危附件'),
    ('esets', u'Esets 病毒'),
    ('sender_whitelist', u'发件人白名单'),
)

REVIEW_RESULT = (
    ('', '--'),
    ('pass', u'通过'),
    ('reject', u'拒绝'),
    ('pass_undo', u'通过(误判处理)'),
    ('reject_undo', u'拒绝(误判处理)'),
    ('c_pass_undo', u'通过(客户-误判处理)'),
    ('c_reject_undo', u'拒绝(客户-误判处理)'),
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
    (9, u'灰名单')
)

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
BULKCUSTOMER_TYPE = (
    ('nomal', u'正常群发'),
    ('evil', u'恶意群发'),
)

CUSTOMER_REPORT = (
    (0, u'无'),
    (1, u'已举报'),
    (2, u'已处理(通过)'),
    (-1, u'已处理(拒绝)')
)

MAIL_SERVERS = (
    ('', u'--'),
    ('shenzhen', u'深圳'),
    ('hangzhou', u'杭州'),
)

REVIEW_STATISTICS_TYPE = (
    ('all', u'全部'),
    ('reviewer', u'审核员'),
)

CREDIT_REASON = (
    ('check_auto_reject', u'免审拒绝'),
    ('check_dspam', u'Dspam'),
    ('send_spam', u'发送垃圾邮件'),
    ('send_not_exist', u'发送不存在邮件'),
    ('review_reject', u'审核拒绝'),
    ('review_pass', u'审核通过'),
)

ERROR_TYPE_DISPLAY = {
    1: u'出站失败，连接异常。',
    2: u'出站失败，收件人地址不存在或无效邮箱。',
    4: u'出站失败，邮件超大或邮箱空间满。',
    5: u'出站失败，垃圾邮件。',
    7: u'出站失败，spf错误。',
    8: u'出站失败，连接超时。'
}


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
        state = models.CharField(u'状态', max_length=20, default='check', choices=MAIL_STATE, db_index=True)
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
        reviewer = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
        review_time = models.DateTimeField(u'审核时间', null=True, blank=True)
        bulk_sample = models.BooleanField(u'是否为群发样本', default=False, db_index=True)
        attach_name = models.TextField(u'所有附件名称，以"----"分开')
        is_del_attach = models.BooleanField(u'是否删除附件', default=False)

        def get_mail_content(self, is_del_attach=None):
            file_path = self.get_mail_path(is_del_attach=is_del_attach)

            if os.path.exists(file_path):
                return open(file_path, 'r').read()

            file_path_old = self.get_mail_path_old()
            if os.path.exists(file_path_old):
                return open(file_path_old, 'r').read()

            # 判断是否需要从其他服务器同步邮件内容
            if self.server_id != settings.SERVER_ID and self.size < get_sync_max_size():
                server = self.server_id.upper()
                url = 'http://{}/mail/send_mail_file?id={}&auth={}'.format(getattr(settings, 'WEB_{}'.format(server)),
                                                                           self.date_id(), get_auth_key())
                try:
                    with open(file_path, 'w') as fw:
                        content = urllib2.urlopen(url).read()
                        fw.write(content)
                    return content
                except IOError, e:
                    return ''
                    # scp(self.get_mail_path(), getattr(settings, 'HOST_{}'.format(server)),
                    # getattr(settings, 'PORT_{}'.format(server)))
            return ''

        def get_mail_path(self, is_del_attach=None):
            file_name = self.get_mail_filename(is_del_attach=is_del_attach)
            return os.path.join(settings.DATA_PATH, db_table, file_name)

        def get_mail_path_old(self):
            try:
                file_name = '{},{},{},{},{}'.format(db_table, self.id, self.customer_id, self.mail_from,
                                                    self.mail_to).replace('/', '')
            except:
                file_name = ''
            return os.path.join(settings.DATA_PATH, db_table, file_name)

        def get_mail_filename(self, is_del_attach=None):
            return '{},{}'.format(db_table, self.id) if not is_del_attach else '{},{}_del_attach'.format(db_table,
                                                                                                         self.id)

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

            # 邮件大小超过某个阀值 且没有删除附件的 发送完成后 直接删除
            max_size = get_max_size()
            if new_state == 'finished' and max_size and self.size >= max_size and not self.is_del_attach:
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
            try:
                redis = get_redis_connection2(self.server_id)
            except:
                redis = get_redis_connection2('default')

            # 保存无效地址
            if self.error_type == 2:
                InvalidMail.objects.get_or_create(mail=self.mail_to.lower())
                # 发件人信誉度处理
                redis.lpush('sender_credit', '{}----{}'.format(self.date_id(), 'send_not_exist'))

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
                # 发件人信誉度处理
                redis.lpush('sender_credit', '{}----{}'.format(self.date_id(), 'send_spam'))

            # spf错误域名 保存到SpfError
            if self.error_type == 7:
                domain = self.mail_from.split('@')[-1]
                SpfError.objects.get_or_create(domain=domain, customer=self.customer)

            if self.error_type in [5, 6]:
                RecipientWhitelist.objects.filter(keyword=self.mail_to).update(disabled=True,
                                                                               operate_time=datetime.datetime.now())


        def get_retry_count(self):
            return DeliverLog.objects.filter(date=self.get_date(), mail_id=self.id).count()


        def clear_mail(self):
            file_path = self.get_mail_path()
            if os.path.exists(file_path):
                os.unlink(file_path)

        def return_message_display(self):
            return u'{}{}'.format(ERROR_TYPE_DISPLAY.get(self.error_type, ''), self.return_message)

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
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater1')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater1')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.domain

    class Meta:
        verbose_name = u'中继发件人域名黑名单'


class SubjectKeywordBlacklist(OrderedModel):
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, blank=True, related_name='children')
    keyword = models.CharField(u'主题关键字', max_length=100, null=False, blank=False,
                               help_text=u"邮件主题如果含有黑名单关键词，则将该邮件挂起并交给管理员审核,支持通配符?，例如“发.{1}票”或“发.{2}票”，这样，则“发a票” 或 “发aa票”")
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    relay = models.BooleanField(u'是否用于中继', default=True)
    direct_reject = models.BooleanField(u'中继,是否不用审核，直接拒绝', default=False)
    collect = models.BooleanField(u'是否用于网关', default=True)
    c_direct_reject = models.BooleanField(u'网关,是否不用审核，直接拒绝', default=False)
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater2')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater2')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)
    relay_all = models.IntegerField(u'中继检测数', default=0)
    relay_pass = models.IntegerField(u'中继通过数', default=0)
    collect_all = models.IntegerField(u'网关检测数', default=0)
    collect_pass = models.IntegerField(u'网关通过数', default=0)

    def __unicode__(self):
        return self.keyword

    def order_by_self(self):
        children = self.children.all().order_by('-order')
        if children:
            move = self.order
            for c in children:
                c.refresh_from_db(fields=('order', ))
                c.to(move)
                move = c.order
            return move
        return None

    class Meta(OrderedModel.Meta):
        verbose_name = u'主题关键字黑名单'

class KeywordBlacklist(OrderedModel):
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, blank=True, related_name='children')
    keyword = models.CharField(u'内容关键字', max_length=100, null=False, blank=False,
                               help_text=u"邮件内容如果含有黑名单关键词，则将该邮件挂起并交给管理员审核,支持通配符?，例如“发.{1}票”或“发.{2}票”，这样，则“发a票” 或 “发aa票”")
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    relay = models.BooleanField(u'是否用于中继', default=True)
    direct_reject = models.BooleanField(u'中继,是否不用审核，直接拒绝', default=False)
    collect = models.BooleanField(u'是否用于网关', default=True)
    c_direct_reject = models.BooleanField(u'网关,是否不用审核，直接拒绝', default=False)
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater3')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater3')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)
    relay_all = models.IntegerField(u'中继检测数', default=0)
    relay_pass = models.IntegerField(u'中继通过数', default=0)
    collect_all = models.IntegerField(u'网关检测数', default=0)
    collect_pass = models.IntegerField(u'网关通过数', default=0)

    def __unicode__(self):
        return self.keyword

    def order_by_self(self):
        children = self.children.all().order_by('-order')
        if children:
            move = self.order
            for c in children:
                c.refresh_from_db(fields=('order', ))
                c.to(move)
                move = c.order
            return move
        return None

    class Meta(OrderedModel.Meta):
        verbose_name = u'内容关键字黑名单'


class CheckSettings(models.Model):
    bulk_max = models.IntegerField(u'群发邮件阀值', null=False, blank=False, default=10,
                                   help_text=u"24小时内,相同主题的邮件超过该值,则被认为是群发邮件")
    bulk_expire = models.IntegerField(u'群发邮件过期天数', null=False, blank=False, default=7,
                                      help_text=u"单位:天数, 如果邮件被认为是群发邮件, 则相应天数里,相同主题将被检测")
    max_size = models.IntegerField(u'邮件最大值', null=False, blank=False, default=50,
                                   help_text=u"单位:M, 能够接收的邮件最大值, 默认50M")
    spam_score_max = models.FloatField(u'中继spam检测分数阀值(白天)', null=False, blank=False, default=5.0,
                                       help_text=u'白天(07:00--19:00)如果spam检测分数超过该阀值, 则被认为是垃圾邮件, 默认为5.0')
    night_spam_score_max = models.FloatField(u'中继spam检测分数阀值(晚上)', null=False, blank=False, default=4.0,
                                             help_text=u'晚上(19:00--07:00)如果spam检测分数超过该阀值, 则被认为是垃圾邮件, 默认为5.0')
    c_spam_score_max = models.FloatField(u'网关spam检测分数阀值(白天)', null=False, blank=False, default=5.0,
                                         help_text=u'白天(07:00--19:00)如果spam检测分数超过该阀值, 则被认为是垃圾邮件, 默认为5.0')
    c_night_spam_score_max = models.FloatField(u'网关spam检测分数阀值(晚上)', null=False, blank=False, default=4.0,
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
    esets_max_size = models.IntegerField(u'Nod32(Esets)检测阀值', null=False, blank=False, default=0,
                                         help_text=u"单位:KB, 邮件如果超过该阀值, 则直接放行, 不进行检测, 默认0KB, 表示全部检测")
    ctasd_max_size = models.IntegerField(u'Ctasd检测阀值', null=False, blank=False, default=0,
                                         help_text=u"单位:KB, 邮件如果超过该阀值, 则直接放行, 不进行检测, 默认0KB, 表示全部检测")
    custom_max_size = models.IntegerField(u'自动回复检测阀值', null=False, blank=False, default=0,
                                          help_text=u"单位:KB, 邮件如果超过该阀值, 则直接放行, 不进行检测, 默认0KB, 表示全部检测")
    attachment_min_size = models.IntegerField(u'高危附件阀值', null=False, blank=False, default=0,
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
    collect_attachment_min_size = models.IntegerField(u'小危附件阀值', null=False, blank=False, default=0,
                                                      help_text=u"单位:KB, 小危附件：自动删除 非中文 邮件中 xxx 附件类型 且 小于XXX KB的邮件，直接删除，不审核，不学习。"
                                                                u"过滤顺序在 发件人白名单检测 之后。 默认0KB, 表示不检测")
    credit = models.IntegerField(u'发件人信誉度检测值', null=False, blank=False, default=1000,
                                 help_text=u"检测中继收件人白名单时，要求 发件人信誉度 高于此设置值")
    hrisk_sender_check_time = models.IntegerField(u'高危发件人检测时间', null=False, blank=False, default=60,
                                                  help_text=u'单位:分钟, 单位时间内，拒绝+发送失败的邮件占邮件总数的比例达到一定比例，'
                                                            u'则在某段时间内拦截其所有邮件，并放入“高危发件人”进行人工审核')
    hrisk_sender_time = models.IntegerField(u'高危发件人拦截时间', null=False, blank=False, default=60,
                                            help_text=u'单位:分钟, 发件人在此段时间内的所有邮件被拦截，并放入“高危发件人”进行人工审核')
    hrisk_sender_scale = models.IntegerField(u'高危发件人高危邮件数占比', null=False, blank=False, default=50,
                                             help_text=u'单位:%, 拒绝+发送失败的邮件占邮件总数的比例，'
                                                       u'达到则在某段时间内拦截其所有邮件，并放入“高危发件人”进行人工审核')
    hrisk_sender_total_num_min = models.IntegerField(u'高危发件人邮件总数最小阀值', null=False, blank=False, default=10,
                                                     help_text=u'单位:个数, 邮件总数超过该最小阀值，且拒绝+发送失败的邮件占邮件总数的比例， '
                                                               u'达到则在某段时间内拦截其所有邮件，并放入“高危发件人”进行人工审核')
    hrisk_diff_sender_count = models.IntegerField(u'名称不同的高危发件人(不同次数)', null=False, blank=False, default=3,
                                                  help_text=u'一天内 同一发件人名称不同值超过N次， 则在以后的M时间内拦截其所有邮件，并放入“高危发件人”进行人工审核')
    hrisk_diff_sender_time = models.IntegerField(u'名称不同的高危发件人(拦截时间)', null=False, blank=False, default=600,
                                                 help_text=u'单位:分钟, 一天内 同一发件人名称不同值超过N次， 则在以后的M时间内拦截其所有邮件，并放入“高危发件人”进行人工审核')


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
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater4')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater4')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)
    relay = models.BooleanField(u'是否用于中继', default=True)
    direct_reject = models.BooleanField(u'中继,是否不用审核，直接拒绝', default=False)
    collect = models.BooleanField(u'是否用于代收', default=True)
    c_direct_reject = models.BooleanField(u'网关,是否不用审核，直接拒绝', default=False)


    def __unicode__(self):
        return self.keyword

    class Meta:
        verbose_name = u'中继主题白名单'


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
    error_type_8 = models.IntegerField(u'发送超时', default=0)
    rate = models.FloatField(u'成功比', default=0)
    ip = models.CharField(u'IP', null=True, blank=True, max_length=20)
    ip_pool = models.ForeignKey(IpPool, null=True, blank=True, on_delete=models.SET_NULL)
    cluster = models.ForeignKey(Cluster, null=True, blank=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING,
                                 related_name='relay_statistics')

    def __unicode__(self):
        return self.date


class SenderBlacklist(OrderedModel):
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, blank=True, related_name='children')
    keyword = models.CharField(u'关键字', max_length=50, null=False, blank=False,
                               help_text=u"收件人如果含有黑名单关键词，则将该邮件挂起,交给管理员审核,支持正则表达式")
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    relay = models.BooleanField(u'是否用于中继', default=True)
    direct_reject = models.BooleanField(u'中继,是否不用审核，直接拒绝', default=False)
    collect = models.BooleanField(u'是否用于代收', default=True)
    c_direct_reject = models.BooleanField(u'网关,是否不用审核，直接拒绝', default=False)
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater5')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater5')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.keyword

    def order_by_self(self):
        children = self.children.all().order_by('-order')
        if children:
            move = self.order
            for c in children:
                c.refresh_from_db(fields=('order', ))
                c.to(move)
                move = c.order
            return move
        return None

    class Meta(OrderedModel.Meta):
        verbose_name = u'发件人关键字黑名单'


class InvalidMail(models.Model):
    mail = models.CharField(u'邮件地址', max_length=150, null=False, blank=False, unique=True, db_index=True,
                            help_text=u"无效邮件地址")
    # disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater6')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater6')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

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
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater7')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater7')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)


    def __unicode__(self):
        return self.keyword

    class Meta:
        verbose_name = u'收件人黑名单'

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
    retry_days = models.IntegerField(u'网关重试天数', default=3, help_text=u'单位：天数，超过该天数的网关邮件不重试发送')
    # max_same_subject = models.IntegerField(u'网关重试天数', default=3, help_text=u'单位：天数，超过该天数的网关邮件不重试发送')
    invalid_mail_expire_days = models.IntegerField(u'无效地址有效期天数', default=30, help_text=u'单位：天数，添加时间超过该天数的无效地址直接删除')
    transfer_max_size = models.IntegerField(u'自动转网络附件最大阀值', default=5, help_text=u'单位：M，邮件大小超过该阀值，则该邮件发送时自动转网络附件')


class SpfError(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True, blank=True)
    domain = models.CharField(u'域名关键字', max_length=200, null=False, blank=False, help_text=u"spf错误域名")
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    status = models.CharField(u'状态', max_length=10, choices=BULKCUSTOMER_STATUS, default='deal')
    note = models.CharField(u'备注', max_length=200, null=True, blank=True, help_text=u"备注")

    def __unicode__(self):
        return self.domain


class CustomKeywordBlacklist(models.Model):
    keyword = models.CharField(u'自动回复关键字', max_length=50, null=False, blank=False,
                               help_text=u"邮件内容或主题如果含有黑名单关键词，则将该邮件挂起并交给管理员审核,支持通配符?，例如“发.{1}票”或“发.{2}票”，这样，则“发a票” 或 “发aa票”")
    type = models.CharField(u'检测类型', max_length=10, choices=CUSTOM_KEYWORD_BLACKLIST_TYPE, default='subject')
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater8')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater8')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)
    relay = models.BooleanField(u'是否用于中继', default=True)
    direct_reject = models.BooleanField(u'中继,是否不用审核，直接拒绝', default=False)
    collect = models.BooleanField(u'是否用于代收', default=True)
    c_direct_reject = models.BooleanField(u'网关,是否不用审核，直接拒绝', default=False)


    def __unicode__(self):
        return self.keyword

    class Meta:
        verbose_name = u'中继自动回复关键字'

class ValidMailSuffix(models.Model):
    keyword = models.CharField(u'邮件后缀名', max_length=50, null=False, blank=False,
                               help_text=u"有效的邮件后缀名")
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater9')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater9')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)


    def __unicode__(self):
        return self.keyword


class AttachmentBlacklist(OrderedModel):
    """
    附件黑名单
    """
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, blank=True, related_name='children')
    keyword = models.CharField(u'附件关键字', max_length=100, null=False, blank=False,
                               help_text=u"对附件进行检测，如果附件名称包含黑名单关键词,　则将邮件标志为高危邮件审核。支持正则")
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    relay = models.BooleanField(u'是否用于中继', default=True)
    direct_reject = models.BooleanField(u'中继,是否不用审核，直接拒绝', default=False)
    collect = models.BooleanField(u'是否用于代收', default=True)
    c_direct_reject = models.BooleanField(u'网关,是否不用审核，直接拒绝', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater10')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater10')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.keyword

    def order_by_self(self):
        children = self.children.all().order_by('-order')
        if children:
            move = self.order
            for c in children:
                c.refresh_from_db(fields=('order', ))
                c.to(move)
                move = c.order
            return move
        return None

    class Meta(OrderedModel.Meta):
        verbose_name = u'附件关键字黑名单'


class AttachmentTypeBlacklist(models.Model):
    """
    网关小危附件类型
    附件黑名单
    """
    keyword = models.CharField(u'小危附件类型', max_length=50, null=False, blank=False,
                               help_text=u"网关小危附件类型，小危附件：自动删除 非中文 邮件中 xxx 附件类型 且 小于XXX KB的邮件，直接删除，不审核，不学习。"
                                         u"过滤顺序在 发件人白名单检测 之后。 ")
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='attach_type_creater')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='attach_type_operater')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.keyword

    class Meta:
        verbose_name = u'网关小危附件类型'


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
    note = models.CharField(u'备注', max_length=200, null=True, blank=True, help_text=u"备注")
    type = models.CharField(u'类型', max_length=10, choices=BULKCUSTOMER_TYPE, default='nomal')


class SenderWhitelist(models.Model):
    sender = models.CharField(u'发件人', max_length=150, null=False, blank=False,
                              help_text=u"发件人白名单 如果发件人在白名单中，跳过后面所有的网关检测, 支持正则标准,支持整域名过滤，"
                                        u"如test.com且下面选中为域名，表示整个test.com为域名的发件人为白名单发件人")
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING)
    is_global = models.BooleanField(u'是否为全局变量', default=False, help_text=u'全局白，是对所有客户生效。客户白，仅仅对这个客户生效')
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    is_domain = models.BooleanField(u'是否为域名', default=False, help_text=u'当选中时，整个域名都为白名单，默认不选中')
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater11')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater11')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)


    def __unicode__(self):
        return self.sender

    class Meta:
        verbose_name = u'网关发件人白名单'

class CustomerSenderBlacklist(models.Model):
    """ 用户发件人黑名单 """
    sender = models.CharField(u'发件人', max_length=150, null=False, blank=False,
                              help_text=u'发件人黑名单:如果发件人在黑名单中，则不进行网关检测直接拒绝, 支持正则标准,支持整域名过滤，'
                                        u'如test.com且下面选中为域名，表示整个test.com为域名的发件人为黑名单发件人')
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING)
    is_global = models.BooleanField(u'是否为全局变量', default=False, help_text=u'全局黑，是对所有客户生效。客户黑，仅仅对这个客户生效')
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    is_domain = models.BooleanField(u'是否为域名', default=False, help_text=u'当选中时，整个域名都为黑名单，默认不选中')
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater110')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater110')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.sender

    class Meta:
        verbose_name = u'网关发件人黑名单'


class InvalidSenderWhitelist(models.Model):
    sender = models.CharField(u'发件人', max_length=150, null=False, blank=False,
                              help_text=u"无效地址发件人白名单 如果发件人在白名单中，跳过中继无效地址检测")
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater12')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater12')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)


    def __unicode__(self):
        return self.sender

    class Meta:
        verbose_name = u'中继无效地址白名单'


class SpfChecklist(models.Model):
    domain = models.CharField(u'域名', max_length=100, null=False, blank=False,
                              help_text=u"强制SPF检查域名库，在此库中的域名强制检查SPF，不论客户是否开启SPF功能. 不支持正则, 格式如：test.com  ,包含所有test.com结尾的域名")
    direct_reject = models.BooleanField(u'是否不用审核，直接拒绝', default=False)
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater13')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater13')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)


    def __unicode__(self):
        return self.domain


class TempSenderBlacklist(models.Model):
    sender = models.CharField(u'发件人', max_length=100, null=False, blank=False,
                              help_text=u"中继临时发件人黑名单, 如果发件人在黑名单中，拒绝连接，不支持正则表达式")
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True, blank=True)
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    expire_time = models.DateTimeField(u'群封过期天数')
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater14')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater14')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)


    def get_status_display(self):
        now = timezone.now()
        if self.expire_time > now:
            return str(self.expire_time - now).split('.', 2)[0]
        else:
            return u'已过期'

    def __unicode__(self):
        return self.sender

    class Meta:
        verbose_name = u'中继临时发件人黑名单'


class RecipientWhitelist(models.Model):
    keyword = models.CharField(u'收件人', max_length=50, null=False, blank=False, unique=True,
                               help_text=u"中继收件人白名单, 如果收件人在白名单中，只做DSPAM过滤，然后就直接发送；"
                                         u"不支持正则标准,支持整域名过滤，如test.com且下面选中为域名，表示整个test.com为域名的收件人为白名单收件人")
    is_domain = models.BooleanField(u'是否为域名', default=False, help_text=u'当选中时，整个域名都为白名单，默认不选中')
    disabled = models.BooleanField(u'是否禁用', default=False)
    hits = models.IntegerField(u'命中次数', default=0)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater15')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater15')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)


    def __unicode__(self):
        return self.keyword

    class Meta:
        verbose_name = u'中继收件人白名单'


class CollectRecipientWhitelist(models.Model):
    keyword = models.CharField(u'收件人', max_length=50, null=False, blank=False, unique=True,
                               help_text=u"网关收件人白名单, 如果收件人在白名单中，网关对该发件人不做任何过滤")
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater30')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater30')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)
    customer = models.ForeignKey(Customer, null=True, blank=True)

    def __unicode__(self):
        return self.keyword

    class Meta:
        verbose_name = u'网关收件人白名单'


class CollectRecipientChecklist(models.Model):
    """
    网关收件人强制检测名单
    """
    keyword = models.CharField(u'收件人', max_length=50, null=False, blank=False, unique=True,
                               help_text=u"网关收件人强制检测名单, 如果收件人在白名单中，该发件人的所有邮件必须强制检测")
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='crc_cr')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='crc_or')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.keyword

    class Meta:
        verbose_name = u'网关收件人强制检测名单'

class CheckStatistics(models.Model):
    """
    发垃圾模块审核率统计
    'active_spam', 'high_risk', 'keyword_blacklist', 'sender_blacklist', 'subject_blacklist', 'cyber_spam', 'spamassassin
    """
    date = models.DateField(u'日期')
    active_spam_all = models.IntegerField(u'动态SPAM全部', default=0)
    active_spam_pass = models.IntegerField(u'动态SPAM通过', default=0)
    high_risk_all = models.IntegerField(u'高危邮件全部', default=0)
    high_risk_pass = models.IntegerField(u'高危邮件通过', default=0)
    keyword_blacklist_all = models.IntegerField(u'内容黑全部', default=0)
    keyword_blacklist_pass = models.IntegerField(u'内容黑通过', default=0)
    sender_blacklist_all = models.IntegerField(u'发件黑全部', default=0)
    sender_blacklist_pass = models.IntegerField(u'发件黑通过', default=0)
    subject_blacklist_all = models.IntegerField(u'主题黑全部', default=0)
    subject_blacklist_pass = models.IntegerField(u'主题黑通过', default=0)
    cyber_spam_all = models.IntegerField(u'cyber全部', default=0)
    cyber_spam_pass = models.IntegerField(u'cyber通过', default=0)
    spamassassin_all = models.IntegerField(u'spam全部', default=0)
    spamassassin_pass = models.IntegerField(u'spam通过', default=0)
    high_sender_all = models.IntegerField(u'高危发件人全部', default=0)
    high_sender_pass = models.IntegerField(u'高危发件人通过', default=0)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)


class ReviewStatistics(models.Model):
    """
    审核统计
    """
    date = models.DateField(u'日期')
    review_all = models.IntegerField(u'全部审核数量', default=0)
    # manual_review = models.IntegerField(u'人工审核数量', default=0)
    # auto_review = models.IntegerField(u'自动审核数量', default=0)
    review_pass = models.IntegerField(u'审核通过数量', default=0)
    review_reject = models.IntegerField(u'审核拒绝数量', default=0)
    review_undo = models.IntegerField(u'审核误判数量', default=0)
    review_pass_undo = models.IntegerField(u'审核误判通过数量', default=0)
    review_reject_undo = models.IntegerField(u'审核误判拒绝数量', default=0)
    times = models.IntegerField(u'平均审核时长，单位为秒', default=0)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)
    type = models.CharField(u'类型', choices=REVIEW_STATISTICS_TYPE, max_length=10, default='all')
    reviewer = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True,
                                 related_name='review_statistics')


class NoticeSettings(models.Model):
    """
    通知设置
    """
    bulk_content = models.TextField(u'群发邮件通知', help_text=u'用户群发邮件的时候通知客户和对应的技术支持,支持变量: {count}表示拒绝数量, {account}表示群发账号')
    bulk_interval = models.IntegerField(u'群发通知间隔', default=60, help_text=u'单位：分钟，群发通知发送间隔时间')
    bulk_count = models.IntegerField(u'群发数量阀值', default=200, help_text=u'用户当天中继的拒绝数量阀值，如果超过该值，则发相应通知')
    review_content = models.TextField(u'审核邮件通知', help_text=u'需审核的邮件超过XXX封（中继+网关-cyber）发送通知给默认审核人员,支持变量: {count}表示审核数量')
    review_interval = models.IntegerField(u'审核通知间隔', default=15, help_text=u'单位：分钟，群发通知发送间隔时间')
    review_count = models.IntegerField(u'审核数阀值', default=200, help_text=u'需审核邮件的封数（中继+网关-cyber），当超过该值时，发送相应通知')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, help_text=u'需通知的默认审核人员', verbose_name=u'默认审核人员',
                                 null=True, blank=True, related_name='reviewer')
    ip_content = models.TextField(u'IP不通通知', help_text=u'当发送机连续10分钟接收邮件都失败时，则通知相应管理员该发送机IP不通,支持变量: {ip}表示发送机IP',
                                  null=True, blank=True)
    ip_interval = models.IntegerField(u'IP不通通知间隔', default=60, help_text=u'单位：分钟，IP不通通知发送间隔时间')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, help_text=u'需通知的默认管理员', verbose_name=u'默认管理员',
                                null=True, blank=True, related_name='manager')
    jam_content = models.TextField(u'服务器拥堵通知',
                                   help_text=u'实时监控服务器处理状态，当中继检测数＋中继传输数＋网关检测数＋网关发送数超过阀值时，发送通知,支持变量: {count}表示总数,'
                                             u'{relay_check}表示中继检测数,{relay_dispatch}表示中继传输数,{collect_check}表示网关检测数,{collect_send}表示网关发送数',
                                   null=True, blank=True)
    jam_interval = models.IntegerField(u'服务器拥堵通知间隔', default=60, help_text=u'单位：分钟，服务器拥堵通知发送间隔时间')
    jam_count = models.IntegerField(u'拥堵阀值', default=200, help_text=u'服务器需处理的邮件封数（中继检测数＋中继传输数＋网关检测数），当超过该值时，发送相应通知')
    collect_content = models.TextField(u'网关用户限制通知',
                                       help_text=u'网关用户收件人数限制，超过就警告管理员和销售,支持变量: {company}(ID：{company_id})表示公司以及公司ID, '
                                                 u'{setting}表示设置的限制值, {count}表示网关收件人数, {account}表示网关收件邮箱', null=True,
                                       blank=True)
    relay_content = models.TextField(u'中继用户限制通知',
                                     help_text=u'中继用户发件人数限制，超过就警告管理员和销售,支持变量: {company}(ID：{company_id})表示公司以及公司ID, '
                                               u'{setting}表示设置的限制值, {count}表示中继发件人数, {account}表示中继发件邮箱', null=True,
                                     blank=True)
    sender_warning_content = models.TextField(u'发件人提醒',
                                              help_text=u'中继邮件审核页面，增加按钮：邮件提醒发件人（发送一封邮件提醒用户在群发垃圾病毒邮件, {mail_from}表示邮件发件人',
                                              null=True, blank=True)
    service_limit_content = models.TextField(u'客户服务到期通知',
                                             help_text=u'中继&网关服务快到期通知客户, {customer}客户名称, {type_info}服务类型(网关/中继) {days}服务即将到期天数, {expire_date}到期日期',
                                             null=True, blank=True)
    c_deliver_exception_content = models.TextField(u'网关客户服务器DOWN机通知',
                                                   help_text=u'网关客户服务器DOWN机提醒管理员和客户管理员, {customer}客户名称, {domain}客户域名, {ip}客户IP')
    c_deliver_exception_interval = models.IntegerField(u'网关客户服务器DOWN机通知间隔', default=60, help_text=u'单位：分钟, 通知发送间隔')


class SenderBlockedRecord(models.Model):
    sender = models.CharField(u'发件人', max_length=100, null=False, blank=False)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING)
    blocked_days = models.IntegerField(u'被封天数', default=0)
    opter = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    opt_time = models.DateTimeField(u'添加时间', auto_now_add=True)


class SpamRptSettings(models.Model):
    html_content = models.TextField(u'垃圾邮件隔离报告模板', help_text=u'将垃圾邮件隔离报告发送给网关用户, 支持变量: {mail_from}表示发件人, 相应字段信息请查看备注栏。')
    m_html_content = models.TextField(u'垃圾邮件隔离报告模板(对管理员)',
                                      help_text=u'将垃圾邮件隔离报告发送给网关管理员, 支持变量: {mail_from}表示发件人, 相应字段信息请查看备注栏。')


class SenderCredit(models.Model):
    """
    中继发件人信誉度
    """
    sender = models.CharField(u'发件人', max_length=150, null=False, blank=False, unique=True)
    credit = models.IntegerField(u'发件人信誉值', default=1000)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)


class SenderCreditLog(models.Model):
    """
    中继发件人信誉度扣除/增加　日志
    """
    sender = models.CharField(u'发件人', max_length=150, null=False, blank=False)
    mail_id = models.CharField(u'邮件ID', max_length=20, null=True, blank=True)
    expect_value = models.IntegerField(u'预计扣除/增加值', default=0)
    value = models.IntegerField(u'实际扣除/增加值', default=0)
    reason = models.CharField(u'原因', max_length=20, null=True, blank=True, choices=CREDIT_REASON)
    create_time = models.DateTimeField(u'创建日期', auto_now_add=True)


class SenderCreditSettings(models.Model):
    """
    中继发件人信誉度设置
    """
    check_auto_reject = models.IntegerField(u'免审拒绝', default=-5, help_text=u'免审拒绝扣除/增加的信誉度值')
    check_dspam = models.IntegerField(u'Dspam', default=-5, help_text=u'被dspam检测扣除/增加的信誉度值')
    send_spam = models.IntegerField(u'发送垃圾邮件', default=-5, help_text=u'发送垃圾邮件扣除/增加的信誉度值')
    send_not_exist = models.IntegerField(u'发送不存在邮件', default=-5, help_text=u'发送不存在邮件扣除/增加的信誉度值')
    review_reject = models.IntegerField(u'审核拒绝', default=-5, help_text=u'审核拒绝扣除/增加的信誉度值')
    review_pass = models.IntegerField(u'审核通过', default=1, help_text=u'审核通过扣除/增加的信誉度值')
    increase_limit = models.IntegerField(u'当天最大增加值', default=10, help_text=u'默认10')
    reduce_limit = models.IntegerField(u'当天最大扣除值', default=100, help_text=u'默认100')


class RelaySenderWhitelist(models.Model):
    ''' 中继发件人白名单 '''
    sender = models.CharField(u'发件人', max_length=150, null=False, blank=False, unique=True,
                              help_text=u'如果发件人在中继发件人白名单中，不进行群发频率限制，不进行任何检测。不支持正则。')
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING)
    note = models.CharField(u'备注', max_length=200, null=True, blank=True, help_text=u"备注")
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater201')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater201')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.sender

    class Meta:
        verbose_name = u'中继发件人白名单'


class CreditIntervalSettings(models.Model):
    ''' 发件人信誉度高于XXX分，执行不同的群发频率检测 '''
    credit_b = models.IntegerField(u'信誉度区间起', null=False, blank=False, default=0,
                                   help_text=u"当发件人信誉度大于等于区间起、小于区间止时，每天可以发送相同主题XX封邮件，XX分钟内允许发送XX封邮件")
    credit_e = models.IntegerField(u'信誉度区间止', null=False, blank=False, default=0,
                                   help_text=u"默认值：0，0表示无穷大")
    bulk_max = models.IntegerField(u'群发邮件阀值', null=False, blank=False, default=10,
                                   help_text=u"24小时内,相同主题的邮件超过该值,则被认为是群发邮件")
    bulk_sender_time = models.IntegerField(u'群发单个发件人监测时间', null=False, blank=False, default=10,
                                           help_text=u'单位：分钟，群发监测单个发件人的时间')
    bulk_sender_max = models.IntegerField(u'群发单个发件人发送阀值', null=False, blank=False, default=10,
                                          help_text=u'单个发件人在监测时间内允许发的邮件封数，超过的接收并丢弃，将邮件数计入群发')


class EdmCheckSettings(models.Model):
    """
    群发系统垃圾检测设置
    SMTP账号发送检测就是用一个或多个smtp账号发送测试，如果返回信息里有垃圾邮件标志，则模板为红色
    检测垃圾的SMTP账号可能会有多个，管理员后台设置格式范例：
    QQ反垃圾检测引擎 smtp.qq.com 56656565@qq.com password 收件人邮箱
    某某反垃圾引擎 smtp.aaa.com  adfb@ss.com password 收件人邮箱
    系统调用上述SMTP账号投递邮件，如果出现 垃圾邮件标志，则返回红色并提示 某某反垃圾引擎 检测为垃圾邮件
    """
    name = models.CharField(u'名称', max_length=50, null=False, blank=False,
                            help_text=u'发垃圾检测引擎名称，如：QQ反垃圾检测引擎, 某某反垃圾检测引擎...')
    smtp_server = models.CharField(u'SMTP服务商', max_length=100, null=False, blank=False,
                                   help_text=u'SMTP服务商地址, 如：smtp.qq.com')
    smtp_port = models.IntegerField(u'SMTP端口', default=25, help_text=u'SMTP服务商端口')
    account = models.CharField(u'SMTP账号', max_length=100, null=False, blank=False, help_text=u'SMTP账号')
    password = models.CharField(u'SMTP密码', max_length=100, null=False, blank=False, help_text=u'SMTP密码')
    receiver = models.CharField(u'收件人邮箱', max_length=100, null=False, blank=False, help_text=u"""
        SMTP账号发送检测就是用一个或多个smtp账号发送测试，如果返回信息里有垃圾邮件标志，则模板为红色
        检测垃圾的SMTP账号可能会有多个，管理员后台设置格式范例：
        QQ反垃圾检测引擎 smtp.qq.com 56656565@qq.com password 收件人邮箱
        某某反垃圾引擎 smtp.aaa.com  adfb@ss.com password 收件人邮箱
        系统调用上述SMTP账号投递邮件，如果出现 垃圾邮件标志，则返回红色并提示 某某反垃圾引擎 检测为垃圾邮件
    """)


class SpamRptBlacklist(models.Model):
    """ 网关隔离报告黑名单 """
    recipient = models.CharField(u'收件人', max_length=150, null=False, blank=False,
                                 help_text=u'隔离报告收件人黑名单:如果收件人在黑名单中，则隔离报告不发送给该发件人')
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING)
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='spam_rpt_blacklist_creater')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='spam_rpt_blacklist_operater')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.recipient

    class Meta:
        verbose_name = u'网关隔离报告收件人黑名单'

class SpfIpWhitelist(models.Model):
    ''' 网关SPF ip白名单 '''
    keyword = models.CharField(u'IP', max_length=150, null=False, blank=False, unique=True,
                              help_text=u'如果发件人来源IP在白名单中，则不进行SPF检测')
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='spfip_creater')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='spfip_operater')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.keyword

    class Meta:
        verbose_name = u'网关SPF ip白名单'

auditlog.register(DomainBlacklist, include_fields=['domain', 'disabled'])
auditlog.register(SubjectKeywordBlacklist,
                  include_fields=['parent', 'keyword', 'is_regex', 'relay', 'direct_reject', 'collect',
                                  'c_direct_reject', 'disabled'])
auditlog.register(KeywordBlacklist,
                  include_fields=['parent', 'keyword', 'is_regex', 'relay', 'direct_reject', 'collect',
                                  'c_direct_reject', 'disabled'])
auditlog.register(SubjectKeywordWhitelist, include_fields=['keyword', 'is_regex', 'disabled'])
auditlog.register(SenderBlacklist,
                  include_fields=['parent', 'keyword', 'is_regex', 'relay', 'direct_reject', 'collect',
                                  'c_direct_reject', 'disabled'])
auditlog.register(RecipientBlacklist, include_fields=['keyword', 'is_regex', 'disabled'])
auditlog.register(CustomKeywordBlacklist, include_fields=['keyword', 'type', 'is_regex', 'disabled'])
auditlog.register(AttachmentBlacklist,
                  include_fields=['parent', 'keyword', 'is_regex', 'relay', 'direct_reject', 'collect',
                                  'c_direct_reject', 'disabled'])
auditlog.register(AttachmentTypeBlacklist, include_fields=['keyword', 'disabled'])
auditlog.register(SenderWhitelist, include_fields=['sender', 'customer', 'is_global', 'is_regex', 'is_domain', 'disabled'])
auditlog.register(CustomerSenderBlacklist, include_fields=['sender', 'customer', 'is_global', 'is_regex', 'is_domain', 'disabled'])
auditlog.register(InvalidSenderWhitelist, include_fields=['sender', 'disabled'])
auditlog.register(TempSenderBlacklist, include_fields=['sender', 'customer', 'disabled', 'expire_time'])
auditlog.register(RecipientWhitelist, include_fields=['keyword', 'is_domain', 'disabled'])
auditlog.register(CollectRecipientWhitelist, include_fields=['keyword', 'disabled'])
auditlog.register(CollectRecipientChecklist, include_fields=['keyword', 'disabled', 'is_regex'])
auditlog.register(RelaySenderWhitelist, include_fields=['sender', 'disabled'])
auditlog.register(SpamRptBlacklist, include_fields=['recipient', 'customer', 'disabled'])
auditlog.register(SpfIpWhitelist, include_fields=['keyword', 'disabled'])
