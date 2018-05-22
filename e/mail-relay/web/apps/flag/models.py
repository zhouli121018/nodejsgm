# coding=utf-8
from django.db import models
from django.contrib.auth.models import User


class NotExistFlag(models.Model):
    keyword = models.CharField(u'收件人不存在标志', max_length=50, null=False, blank=False,
                               help_text=u"邮箱不存在标志, 发送邮件返回信息中包含此内容, 则认为收件人不存在")
    relay = models.BooleanField(u'是否用于中继', default=True)
    collect = models.BooleanField(u'是否用于代收', default=True)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater16')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater16')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.keyword


class BigQuotaFlag(models.Model):
    keyword = models.CharField(u'超大/满的邮件标志', max_length=50, null=False, blank=False,
                               help_text=u"超大/满的邮件标志, 发送邮件返回信息中包含此内容, 则认为是超大/满的邮件")
    relay = models.BooleanField(u'是否用于中继', default=True)
    collect = models.BooleanField(u'是否用于代收', default=True)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater17')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater17')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.keyword


class SpamFlag(models.Model):
    keyword = models.CharField(u'垃圾邮件标志', max_length=50, null=False, blank=False,
                               help_text=u"垃圾邮件标志, 发送邮件返回信息中包含此内容, 则认为该邮件为垃圾邮件")
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    relay = models.BooleanField(u'是否用于中继', default=True)
    collect = models.BooleanField(u'是否用于代收', default=True)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater18')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater18')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.keyword


class NotRetryFlag(models.Model):
    keyword = models.CharField(u'不重试邮件标志', max_length=50, null=False, blank=False,
                               help_text=u"不重试邮件标志, 发送邮件返回信息中包含此内容, 则该邮件不重试")
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    relay = models.BooleanField(u'是否用于中继', default=True)
    collect = models.BooleanField(u'是否用于代收', default=True)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater19')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater19')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.keyword

class SpfFlag(models.Model):
    keyword = models.CharField(u'spf错误邮件标志', max_length=50, null=False, blank=False,
                               help_text=u"spf邮件标志, 发送邮件返回信息中包含此内容, 则认为是spf错误邮件")
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    relay = models.BooleanField(u'是否用于中继', default=True)
    collect = models.BooleanField(u'是否用于代收', default=True)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater20')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater20')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.keyword


class HighRiskFlag(models.Model):
    """
    高危附件　文件类型
    """
    keyword = models.CharField(u'高危附件标志', max_length=50, null=False, blank=False,
                               help_text=u"高危附件标志, 对附件进行监控，附件的类型可定义，比如js、vbs等。含有此类附件的邮件放入高危邮件审核。")
    relay = models.BooleanField(u'是否用于中继', default=True)
    collect = models.BooleanField(u'是否用于代收', default=True)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater21')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater21')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.keyword

class GreyListFlag(models.Model):
    """
    灰名单列表
    """
    keyword = models.CharField(u'灰名单标志', max_length=50, null=False, blank=False,
                               help_text=u"灰名单标志, 发送邮件返回信息中包含此内容, 则认为是灰名单邮件")
    relay = models.BooleanField(u'是否用于中继', default=True)
    collect = models.BooleanField(u'是否用于代收', default=True)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='greylist_creater')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='greylist_operater')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)

    def __unicode__(self):
        return self.keyword
