#coding=utf-8
from django.db import models

CUSTOMER_STATUS = (
    ('', u'--'),
    ('normal', u'正常'),
    ('expired', u'过期'),
    ('disabled', u'禁用')

)

class ColCustomer(models.Model):
    username = models.CharField(u'客户帐号', max_length=50, null=False, blank=False, unique=True)
    password = models.CharField(u'密码', max_length=128, null=True, blank=True)
    company = models.CharField(u'公司名称', max_length=100, null=False, blank=False, unique=True)
    service_start = models.DateField(u'服务开始时间')
    service_end = models.DateField(u'服务到期时间')
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    status = models.CharField(u'状态', max_length=10, default="normal", choices=CUSTOMER_STATUS)

    def __unicode__(self):
        return u'{}({})'.format(self.company, self.username)

    def save(self, *args, **kwargs):
        disabled = True if self.status == 'disabled' else False
        ColCustomerDomain.objects.filter(customer_id=self.id).update(disabled=disabled)
        super(ColCustomer, self).save(*args, **kwargs)
        if not ColCustomerSetting.objects.filter(customer=self):
            ColCustomerSetting.objects.create(customer=self)


class ColCustomerDomain(models.Model):
    customer = models.ForeignKey(ColCustomer, related_name='domain')
    domain = models.CharField(u'客户域名', max_length=100, null=False, blank=False)
    forward_address = models.CharField(u'转发地址', max_length=100, null=False, blank=False)
    disabled = models.BooleanField(u'是否禁用', default=False)

    def save(self, *args, **kwargs):
        self.domain = self.domain.lower()
        super(ColCustomerDomain, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.domain

class ColCustomerSetting(models.Model):
    customer = models.ForeignKey(ColCustomer, related_name='setting')
    check_dspam = models.BooleanField(u'dspam过滤', default=True)
    check_ctasd = models.BooleanField(u'cyber过滤', default=True)
    check_sender = models.BooleanField(u'发件人黑名单过滤', default=True)
    check_subject = models.BooleanField(u'主题关键字过滤', default=True)
    check_content = models.BooleanField(u'内容关键字过滤', default=True)
    check_spam = models.BooleanField(u'spamassassion过滤', default=True)
    check_high_risk = models.BooleanField(u'高危邮件过滤', default=True)

