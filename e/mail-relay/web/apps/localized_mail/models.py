#coding=utf-8
import os
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from apps.core.models import Customer


CHECK_RESULT = (
    ('', '--'),
    ('high_risk', u'高危邮件'),
    ('sender_blacklist', u'发件黑'),
    ('keyword_blacklist', u'内容黑'),
    ('subject_blacklist', u'主题黑'),
    ('subject_and_keyword', u'主题和内容关键字'),
    ('cyber_spam', u'CYBER-Spam'),
    ('spamassassin', u'垃邮(spamassassin)'),
    ('error', u'检测出错'),
    ('c_sender_blacklist', u'发件人黑名单'),
)

MAIL_STATE = (
    ('', '--'),
    ('review', u'等待审核'),
    ('pass', u'审核已通过'),
    ('reject', u'审核已拒绝'),
    ('passing', u'审核通过中'),
    ('rejecting', u'审核拒绝中'),
)
MAIL_ORIGIN = (
    ('', '--'),
    ('collect', u'网关'),
    ('relay', u'中继'),
)

class LocalizedMail(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True, blank=True)
    check_result = models.CharField(u'检测结果', max_length=20, null=True, blank=True, choices=CHECK_RESULT, db_index=True)
    check_message = models.TextField(u'检测详细结果', null=True, blank=True)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    mail_from = models.CharField(u'发件人', max_length=150, null=True, blank=True)
    mail_to = models.CharField(u'收件人', max_length=150, null=True, blank=True)
    subject = models.CharField(u'主题', max_length=800, null=True, blank=True)
    state = models.CharField(u'状态', max_length=20, default='review', choices=MAIL_STATE, db_index=True)
    size = models.IntegerField(u'邮件大小', default=0)
    reviewer = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    review_time = models.DateTimeField(u'审核时间', null=True, blank=True)
    mail_id = models.CharField(u'客户邮件ID', max_length=20, null=True, blank=True)
    origin = models.CharField(u'来源', max_length=20, choices=MAIL_ORIGIN, default='collect', db_index=True)
    created_date = models.DateField(u'创建日期', auto_now_add=True, db_index=True)

    def get_mail_content(self):
        file_path = self.get_mail_path()
        return open(file_path, 'r').read() if os.path.exists(file_path) else ''

    def get_mail_path(self):
        print os.path.join(settings.DATA_LOCALIZED_PATH, str(self.id))
        return os.path.join(settings.DATA_LOCALIZED_PATH, str(self.id))
