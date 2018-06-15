# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from app.core.models import Customer
from app.task.models import SendTask
from app.address.models import MailList
from app.template.models import SendTemplate
from app.trigger.utils import const
from django.db.models import Q
class TriggerHoliday(models.Model):
    """
    触发器节假日选择
    """
    name = models.CharField(u'节假日名称', max_length=20, null=False, blank=False)
    date = models.DateField(u"节假日期", null=True, blank=True, help_text=u"指定触发的节假日")
    status = models.CharField(_(u'状态'), max_length=10, null=False, blank=False, choices=const.TRIGGER_STATUS, default="enable")

    class Meta:
        managed = False
        db_table = 'trigger_holiday'

class Trigger(models.Model):
    """ 触发器
    """
    customer = models.ForeignKey(Customer, null=False, blank=False, db_index=True)
    name = models.CharField(_(u'触发器名称'), max_length=50, null=False, blank=False)
    type = models.CharField(_(u'触发器类型'), max_length=20, null=False, blank=False, choices=const.TRIGGER_TYPE)
    status = models.CharField(_(u'状态'), max_length=10, null=False, blank=False, choices=const.TRIGGER_STATUS, default="enable")
    maillist_type = models.CharField(_(u'地址分类类型'), max_length=10, null=False, blank=False, default='all', choices=const.MAILLIST_TYPE)
    expire_type = models.CharField(_(u'有效期类型'), max_length=10, null=False, blank=False, default='forever', choices=const.EXPIRE_TYPE)
    start_time = models.DateTimeField(u'开始时间', null=True, blank=True)
    end_time = models.DateTimeField(u'结束时间', null=True, blank=True)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(u'修改时间', null=True, auto_now=True)
    trigger_maillists = models.ManyToManyField(
        MailList,
        verbose_name='trigger maillists',
        blank=True,
        help_text=u'触发器选择收件人列表.',
        related_name="trigger_set",
        related_query_name="trigger",
        through='TriggerListShip',
    )
    tasks = models.ManyToManyField(
        SendTask,
        verbose_name='trigger',
        blank=True,
        help_text=u'任务对应的触发器列表.',
        related_name="trigger_set",
        related_query_name="trigger",
        through='TriggerSendtaskShip',
    )
    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if isinstance(self.end_time, basestring):
            self.end_time = datetime.datetime.strptime(self.end_time, '%Y-%m-%d')
        if self.expire_type == 'custom' and timezone.now() > self.end_time:
            self.status = 'expired'
        super(Trigger, self).save(*args, **kwargs)

    class Meta:
        managed = False
        db_table = 'trigger'

    @property
    def shortname(self):
        if len(self.name)<=30:
            return self.name
        return self.name[:30] + "..."

    def enable_trigger_action(self):
        return self.trigger_action.filter(status='enable')

    @staticmethod
    def getTriggerBylist(user_id, list_id, type=None):
        if type:
            ids = TriggerListShip.objects.filter(maillist_id=list_id, trigger__type=type, trigger__status="enable").values_list("trigger_id", flat=True)
            q = Q(customer_id=user_id, maillist_type="all", status="enable", type=type)
        else:
            ids = TriggerListShip.objects.filter(maillist_id=list_id, trigger__status="enable").values_list("trigger_id", flat=True)
            q = Q(customer_id=user_id, maillist_type="all", status="enable")
        return Trigger.objects.filter(customer_id=user_id).filter( Q(id__in=ids) |  q)

    @staticmethod
    def getTriggerBylistids(user_id, list_ids, type=None):
        if type:
            lists = TriggerListShip.objects.filter(trigger__type=type, trigger__status="enable")
            for list_id in list_ids:
                lists = lists.filter(maillist_id=list_id)
            ids = lists.values_list("trigger_id", flat=True)
            # ids = TriggerListShip.objects.filter(maillist_id__in=list_ids, trigger__type=type, trigger__status="enable").values_list("trigger_id", flat=True)
            q = Q(customer_id=user_id, maillist_type="all", status="enable", type=type)
        else:
            lists = TriggerListShip.objects.filter(trigger__type=type, trigger__status="enable")
            for list_id in list_ids:
                lists = lists.filter(maillist_id=list_id)
            ids = lists.values_list("trigger_id", flat=True)
            # ids = TriggerListShip.objects.filter(maillist_id__in=list_ids, trigger__status="enable").values_list("trigger_id", flat=True)
            q = Q(customer_id=user_id, maillist_type="all", status="enable")
        return Trigger.objects.filter(customer_id=user_id).filter( Q(id__in=ids) |  q)

    def get_maillist_ids(self):
        if self.maillist_type == 'all':
            lists = MailList.objects.filter(customer=self.customer, isvalid=True, is_smtp=False).values_list('id', flat=True)
        else:
            lists = TriggerListShip.objects.filter(trigger=self).values_list('maillist', flat=True)
        return lists


class TriggerListShip(models.Model):
    """ 触发器与邮件列表的对应关系
    """
    trigger = models.ForeignKey(Trigger, db_index=True)
    maillist = models.ForeignKey(MailList, db_column="list_id", db_index=True)

    class Meta:
        managed = False
        auto_created = True
        db_table = 'trigger_list_ship'


class TriggerSendtaskShip(models.Model):
    """ 触发器与邮件列表的对应关系
    """
    task = models.ForeignKey(SendTask, db_index=True)
    trigger = models.ForeignKey(Trigger, db_index=True)

    class Meta:
        managed = False
        auto_created = True
        db_table = 'trigger_sendtask_ship'

class TriggerAction(models.Model):
    """ 触发器动作
    """
    trigger = models.ForeignKey(Trigger, related_name="trigger_action", null=True, blank=True)
    action_name = models.CharField(u'动作名称', max_length=50, null=True, blank=True)
    condition = models.CharField(u'触发条件', max_length=20, null=True, blank=True, choices=const.TRIGGER_CONDITION)
    con_url = models.CharField(u"点击的URL", max_length=500, null=True, blank=True, help_text=u"可以为空，空表示所有点击的动作都会触发，如果有值，表示只有点击的链接包含了该值才会触发")
    con_url_template = models.ForeignKey(SendTemplate, related_name='con_url_template', db_index=True, null=True, blank=True, help_text=u'模板名称')
    # con_holiday = models.CharField(u'节假日选择器', max_length=20, null=True, blank=True, help_text=u'事先在后台配置好的节假日期')
    con_holiday = models.ForeignKey(TriggerHoliday, null=True, blank=True, help_text=u'事先在后台配置好的节假日期')
    con_holiday_date = models.DateField(u"节假日期", null=True, blank=True, help_text=u"指定触发的节假日")
    action_schedule = models.CharField(u'触发时间类型', max_length=20, null=False, blank=False, default='immediately', choices=const.ACTION_SCHEDULE)
    action_time = models.IntegerField(u'触发时间', default=0, help_text=u'用户输入的时间,需跟下面的单位时间结合')
    time_type = models.CharField(u'时间单位', max_length=10, null=False, blank=False, default='hou', choices=const.TIME_TYPE)
    t_action_time = models.IntegerField(u'触发时间', default=0, help_text=u'统一转换为多少分钟')
    template = models.ForeignKey(SendTemplate, db_index=True, related_name='template', null=False, blank=False, help_text=u'模板名称')
    send_acct_domain = models.CharField(u'发送账号域名', null=False, blank=False, max_length=60, default='all')
    send_acct_address = models.CharField(u'发送地址', null=False, blank=False, max_length=100)
    replyto = models.CharField(u'指定回复地址', null=True, blank=True, max_length=100)
    sendname = models.CharField(u'发送人名称', null=True, blank=True, max_length=50)
    status = models.CharField(u'状态', null=True, blank=True, max_length=10, choices=const.TRIGGERACTION_STATUS, default='enable')

    # track_status = models.SmallIntegerField(u'邮件跟踪', default=0, choices=const.TRACK_STATUS)
    # track_domain = models.CharField(u'跟踪统计域名', null=True, blank=True, max_length=100,
    #                                 help_text=u'推荐使用自有域名，将该域名的CNAME记录指向count.bestedm.org；默认使用随机域名(xxx.count.bestedm.org) xxx为随机字符串')

    # trigger_templates = models.ManyToManyField(
    #     SendTemplate,
    #     verbose_name='trigger action templates',
    #     blank=True,
    #     help_text=u'触发器选择模板列表.',
    #     related_name="trigger_action_template_set",
    #     related_query_name="trigger_action",
    #     through='TriggerTemplateShip',
    # )
    def save(self, *args, **kwargs):
        t_action_time = 0
        if self.action_time:
            t = 1
            if self.time_type == 'hou':
                t = 60
            if self.time_type == 'day':
                t = 60 * 24
            t_action_time = int(self.action_time) * t
        if self.action_schedule == 'delay':
            self.t_action_time = t_action_time
        elif self.action_schedule == 'advance':
            self.t_action_time = -t_action_time
        else:
            self.t_action_time = 0
        super(TriggerAction, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.get_condition_display()

    class Meta:
        managed = False
        db_table = 'trigger_action'


# class TriggerTemplateShip(models.Model):
#     """ 触发器动作与模板的对应关系
#     """
#     action = models.ForeignKey(TriggerAction, db_index=True)
#     template = models.ForeignKey(SendTemplate, db_index=True)
#
#     class Meta:
#         managed = False
#         auto_created = True
#         db_table = 'trigger_template_ship'


class TriggerTask(models.Model):
    """ 触发器任务
    """
    name = models.CharField(u'任务名称', max_length=50, null=False, blank=False)
    customer = models.ForeignKey(Customer)
    send_task = models.ForeignKey(SendTask, null=True, blank=True)
    trigger = models.ForeignKey(Trigger, null=True, blank=True)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.trigger.type == 'holiday':
            self.name = "h-{}-{}".format(self.customer.id, self.trigger.id)
        elif self.trigger.type == 'birthday':
            self.name = "b-{}-{}".format(self.customer.id, self.trigger.id)
        else:
            self.name = "t-{}-{}-{}".format(self.customer.id, self.send_task.id, self.trigger.id)
        super(TriggerTask, self).save(*args, **kwargs)

    class Meta:
        managed = False
        db_table = 'trigger_task'
        unique_together = (('send_task', "trigger"),)


class TriggerTaskOne(models.Model):
    """
    单个触发任务
    """
    trigger_task = models.ForeignKey(TriggerTask)
    trigger_action = models.ForeignKey(TriggerAction)
    email = models.CharField(u'邮箱', max_length=200, null=False, blank=False)
    status = models.CharField(u'状态', max_length=10, default='wait', choices=const.TRIGGER_TASK_STATUS)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    action_time = models.DateTimeField(u'动作时间', null=True, blank=True)

    def saveStatus(self, status='done'):
        self.status = status
        self.save()

    class Meta:
        managed = False
        db_table = 'trigger_task_one'



