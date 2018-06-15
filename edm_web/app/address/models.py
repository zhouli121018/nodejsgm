#coding=utf-8
from __future__ import unicode_literals

from django.db import models
from app.core.models import Customer, Manager
from app.template.models import SendTemplate, SendSubject
from app.task.models import SendTask

from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

IS_UPSET_FLAG = (
    ('1', u'未打乱'),
    ('2', u'正在打乱'),
    ('3', u'成功打乱'),
    ('4', u'打乱异常'),
)

ADDRESS_IMPORT_STATUS = (
    ('-1', _(u'等待导入')),
    ('0', _(u'正在导入')),
    ('1', _(u'导入成功')),
    ('-2', _(u'导入失败')),
)

MAIL_STORE_STATUS = (
    ('1', u'未入库'),
    ('2', u'预入库'),
    ('3', u'正在入库'),
    ('4', u'已入库'),
)

class MailList(models.Model):
    """
    地址池分类
    """
    id = models.AutoField(primary_key=True, db_column='list_id')
    customer = models.ForeignKey(Customer, related_name='maillist_customer', db_index=True, null=False, blank=False)
    subject = models.CharField(_(u'联系人分类名称'), null=True, blank=True, max_length=35)
    description = models.CharField(_(u'备注'), max_length=500, null=True, blank=True)
    created = models.DateTimeField(_(u'创建时间'), auto_now_add=True)
    updated = models.DateTimeField(_(u'修改时间'), null=True)
    isvalid = models.BooleanField(_(u'是否有效'), default=True)
    count_all = models.IntegerField(u"地址总量", default=0, help_text=u'总地址 - 重复地址')
    count_err = models.IntegerField(u"无效地址", default=0, help_text=u'格式错误邮件 + 无效地址库命中的地址')
    count_real = models.IntegerField(u"实际地址数量", default=0)
    count_subscriber = models.IntegerField(u"订阅地址数量", default=0)
    count_complaint = models.IntegerField(u"投诉数量", default=0)
    # count_unsubscribe = models.IntegerField(u"退订地址数量", default=0)
    last_in_status = models.BooleanField(u'最后入库状态', default=False, help_text=u'True表示正在入库。')
    is_allow_export = models.BooleanField(u'开启导出按钮', default=True, help_text=u'地址池导出功能，1为开启，0为禁用，默认为1, 区别是否共享地址池, 共享地址池为False')
    is_smtp = models.BooleanField(u'是否为smtp发送邮箱', default=False, help_text=u'SMTP发送保存的邮件,对客户不显示')
    is_upset_flag = models.CharField(u'共享地址打乱标志', null=False, blank=False, choices=IS_UPSET_FLAG, max_length=1, default="0")

    status = models.CharField(u'入库状态', null=False, blank=False, choices=MAIL_STORE_STATUS, max_length=1, default="1", help_text=u'客服将客户地址入库的状态')
    in_date = models.DateTimeField(u'预入库时间', null=True)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, related_name='maillist_manager', db_index=True, null=True, blank=True)
    is_importing = models.BooleanField(u'是否正在导入', default=False, help_text=u'是否正在导入地址')
    is_shield = models.BooleanField(_(u'是否被屏蔽'), default=False)
    used_count = models.IntegerField(u"使用次数", default=0)
    last_used = models.DateTimeField(u"最后使用时间", null=True)
    # ALTER TABLE `ml_maillist` ADD `used_count` INT( 11 ) NOT NULL DEFAULT '0' COMMENT '使用次数', ADD `last_used` DATETIME NULL DEFAULT NULL COMMENT '最后使用时间'；

    # 无效地址率
    def get_invalid_rate(self):
        if self.count_all:
            return "{}%".format(round( ( self.count_err*100.00/self.count_all ), 2) )
        return '0%'

    def get_log_info(self):
        obj = self.maillistlog_mailList.all().first()
        if obj:
            return obj.last_in_time, obj.last_in_count
        return None, None

    def get_log_time(self):
        return self.get_log_info()[0]

    def get_log_count(self):
        return self.get_log_info()[1]

    def __unicode__(self):
        return self.subject

    class Meta:
        managed = False
        db_table = 'ml_maillist'

# 地址池和任务的关联表
class TaskMailList(models.Model):
    send = models.ForeignKey(SendTask)
    maillist = models.ForeignKey(MailList)

    class Meta:
        auto_created = True
        db_table = 'ms_send_maillist'

class MailListLog(models.Model):
    """
    入库日志
    """
    customer = models.ForeignKey(Customer, related_name='maillistlog_customer', db_index=True, null=False, blank=False)
    maillist = models.ForeignKey(MailList, related_name='maillistlog_mailList', db_index=True, null=False, blank=False)
    last_in_status = models.BooleanField(u'最后入库状态', default=False, help_text=u'True表示正在入库。')
    tag_count = models.IntegerField(u'标签数量', default=0)
    in_count = models.IntegerField(u'入库地址量', default=0)
    repeat_count = models.IntegerField(u'重复地址数', default=0)
    last_in_count = models.IntegerField(u"成功入库地址量", default=0)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, related_name='maillistlog_manager', db_index=True, null=True, blank=True)
    last_in_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(u'修改时间', null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'ml_maillist_log'


class AddressImportLog(models.Model):
    """
    地址池导入日志
    """
    customer = models.ForeignKey(Customer, related_name='maillist_customer02', db_index=True, null=False, blank=False)
    maillist_id = models.IntegerField(_(u"分类ID"),default=0)
    filename = models.CharField(_(u'文件名称'), null=True, blank=True, max_length=50)
    filepath = models.CharField(_(u'保存路径'), null=True, blank=True, max_length=100)
    time_upload = models.DateTimeField(_(u"上传时间"), null=True, blank=True, auto_now_add=True)
    time_import = models.DateTimeField(_(u"导入时间"), null=True, blank=True)
    time_finish = models.DateTimeField(_(u"完成时间"), null=True, blank=True)
    count_all = models.IntegerField(_(u"地址总量"), default=0)
    count_err_1 = models.IntegerField(_(u"无效地址"), default=0)
    count_err_2 = models.IntegerField(_(u"重复地址"), default=0)
    status = models.CharField(_(u'状态'), null=False, blank=False, choices=ADDRESS_IMPORT_STATUS, max_length=1, default="-1")
    is_disorder = models.BooleanField(_(u'是否打乱导入'), default=False)
    is_newimport = models.BooleanField(_(u'是否新系统地址导入'), default=False)
    is_ignore = models.BooleanField(_(u'是否忽略文件第一行'), default=False)

    def count_success(self):
        return self.count_all - self.count_err_1 - self.count_err_2

    def maillist(self):
        try:
            return MailList.objects.get(id=self.maillist_id).subject if self.maillist_id else _(u'未分类地址')
        except:
            return ''

    def __unicode__(self):
        return self.filename

    class Meta:
        managed = False
        db_table = 'ml_import'

class ComplaintList(models.Model):
    """
    地址投诉记录
    """
    address = models.CharField(_(u'投诉地址'), null=True, blank=True, max_length=50, unique=True)
    created = models.DateTimeField(_(u'创建时间'), auto_now_add=True)
    customer = models.ForeignKey(Customer, related_name='maillist_customer03', db_index=True, null=True, blank=True)
    template = models.ForeignKey(SendTemplate, related_name='maillist_template01', null=True, blank=True)
    subject = models.CharField(_(u'邮件主题'), null=True, blank=True, max_length=100)
    task = models.ForeignKey(SendTask, related_name='maillist_task01', null=True, blank=True)

    def __unicode__(self):
        return self.address

    class Meta:
        managed = False
        db_table = 'ml_complaintlist'


FILTER_TYPE = (
    ('name', u'姓名'),
    ('mobilephone', u'移动电话'),
    ('telephone', u'固定电话'),
    ('company_name', u'公司(学校)'),
    ('post_name', u'岗位名称'),
    ('profession', u'专业名称'),
)

class MailExcludeRule(models.Model):
    ''' 邮箱变量值排除规则 '''
    keyword = models.CharField(u'关键字', max_length=500, null=False, blank=False,
                               help_text=u"邮箱变量值如果含有关键字，则过滤该变量值,支持正则表达式")
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    disabled = models.BooleanField(u'是否禁用', default=False)

    def __unicode__(self):
        return self.keyword

    class Meta:
        managed = False
        db_table = 'mail_exclude_rule'


class MailFilterRule(models.Model):
    ''' 邮箱字段过滤规则 '''
    keyword = models.CharField(u'关键字', max_length=200, null=False, blank=False, help_text=u"关键字过滤邮箱变量值,支持正则表达式")
    filter_type = models.CharField(u'过滤类型', max_length=20, null=False, blank=False, choices=FILTER_TYPE)
    is_regex = models.BooleanField(u'是否支持正则', default=False)
    disabled = models.BooleanField(u'是否禁用', default=False)
    remark = models.CharField(u'备注',max_length=500, null=True, blank=True, help_text=u'关键字的描述信息')

    def __unicode__(self):
        return self.keyword

    class Meta:
        managed = False
        db_table = 'mail_filter_rule'
        unique_together = (('keyword', "filter_type"),)


class RecipientBlacklist(models.Model):
    ''' 收件人黑名单 '''
    user = models.ForeignKey(Customer, related_name='customer_rcpblack', db_index=True, null=False, blank=False)
    addr = models.CharField(u'地址', max_length=100, null=False, blank=False, db_index=True,
                            help_text=u"当对象为邮箱时请在“地址”里填写邮件地址，对象为域时请在“地址”中填写“@域名”，eg:“@test.com”")
    created = models.DateTimeField(u'创建时间', auto_now_add=True)

    def __unicode__(self):
        return self.addr

    class Meta:
        managed = False
        db_table = 'ml_rcpblacklist'
        unique_together = (('user', "addr"),)


class ShareMailList(models.Model):
    """  母账户单向的向子账户共享 地址池
    子账户只能查看以及使用母账户地址池，以及删除关系
    """
    maillist = models.ForeignKey(MailList, null=False, blank=False, related_name="sub_share_maillist", on_delete=models.CASCADE)
    # 共享给目标用户id
    user = models.ForeignKey(Customer, related_name="sub_share_maillist_user", null=False, blank=False, db_index=True, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "ml_maillist_share"
        unique_together = (('maillist', "user"),)
