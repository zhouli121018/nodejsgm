#coding=utf-8
from __future__ import unicode_literals
from django.db import models
from app.core.models import Customer


class StatTask(models.Model):
    """
    任务统计
    """
    id = models.AutoField(primary_key=True, db_column='task_id')
    customer = models.ForeignKey(Customer, related_name='track_Customer03', null=False, blank=False, db_index=True)
    task_date = models.DateField(u'任务时间', null=False, default='0000-00-00', db_index=True)
    task_ident = models.CharField(u'任务名称', null=True, blank=True, max_length=64, db_index=True)
    count_send = models.IntegerField(u'发送总数', default=0)
    count_error = models.IntegerField(u'投递失败', default=0)
    count_err_1 = models.IntegerField(u'邮箱不存在', default=0)
    count_err_2 = models.IntegerField(u'空间不足', default=0)
    count_err_3 = models.IntegerField(u'用户拒收', default=0)
    count_err_5 = models.IntegerField(u'拒绝投递', default=0)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    refunded = models.SmallIntegerField(u'返点', null=False, blank=False, default=0, help_text='record refund for new edm system')
    t_count_error = models.IntegerField(u'错误', null=False, blank=False, default=0)
    rebate = models.IntegerField(u'回扣', null=False, blank=False, default=0)

    class Meta:
        managed = False
        unique_together = (("customer", "task_ident", "task_date"),)
        db_table = 'stat_task'


class StatTaskReal(models.Model):
    """
    任务统计 真实数据
    """
    customer = models.ForeignKey(Customer, related_name='track_StatTaskReal', null=False, blank=False, db_index=True)
    task_ident = models.CharField(u'任务名称', null=True, blank=True, max_length=64, db_index=True)
    domain = models.CharField(u'收件人域名', max_length=100, null=False, blank=False, help_text=u'*代表其他域名')
    count_send = models.IntegerField(u'发送总数', default=0)
    count_error = models.IntegerField(u'投递失败', default=0)
    count_err_1 = models.IntegerField(u'邮箱不存在', default=0)
    count_err_2 = models.IntegerField(u'空间不足', default=0)
    count_err_3 = models.IntegerField(u'用户拒收', default=0)
    count_err_5 = models.IntegerField(u'拒绝投递', default=0)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(u'修改时间', null=True, auto_now=True)

    class Meta:
        managed = False
        unique_together = (("customer", "task_ident", "domain"),)
        db_table = 'stat_task_real'

class StatTaskSettings(models.Model):
    task_count = models.IntegerField(u'任务数量', default=10, help_text=u'至少10个任务取平均成功率。')
    send_count = models.IntegerField(u'发送数量', default=100, help_text=u'每个任务发送数量至少100。')
    domain = models.TextField(u'域名', null=True, blank=True, help_text=u'维护待统计的域名列表，每一行维护一个')

    class Meta:
        managed = False
        db_table = 'stat_task_setting'

class CoreCustomerScore(models.Model):
    """
    最近 10个任务的平均成功率
    """
    customer = models.ForeignKey(Customer, related_name='track_CoreCustomerScore', null=False, blank=False, unique=True)
    domain = models.CharField(u'收件人域名', max_length=100, null=False, blank=False, help_text=u'*代表客户所有域名的分数')
    score = models.DecimalField(u'分数', max_digits=5, decimal_places=2, default=0, help_text=u'成功率*100, 四舍五入')
    score_s = models.DecimalField(u'分数(除去拒绝投递)', max_digits=5, decimal_places=2, default=0, help_text=u'成功率*100, 四舍五入')
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(u'修改时间', null=True, auto_now=True)

    class Meta:
        managed = False
        unique_together = (("customer", "domain"),)
        db_table = 'core_customer_score'


class TrackStat(models.Model):
    """
    邮件打开跟踪
    """
    id = models.AutoField(primary_key=True, db_column='track_id')
    task_ident = models.CharField(u'任务名称', null=True, blank=True, max_length=64, db_index=True)
    customer = models.ForeignKey(Customer, related_name='track_Customer01', null=False, blank=False, db_index=True)
    open_unique = models.IntegerField(u'唯一打开数', null=False, blank=False, default=0)
    open_total = models.IntegerField(u'总打开数', null=False, blank=False, default=0)
    open_first = models.DateTimeField(u'首次打开时间', null=True, auto_now=True)
    open_last = models.DateTimeField(u'最后打开时间', null=True, auto_now=True)
    click_unique = models.IntegerField(u'唯一点击数', null=False, blank=False, default=0)
    click_total = models.IntegerField(u'总点击数', null=False, blank=False, default=0)
    click_first = models.DateTimeField(u'首次点击时间', null=False, blank=False, default=0)
    click_last = models.DateTimeField(u'最后点击时间', null=False, blank=False, default=0)
    content_id = models.IntegerField(u'模板内容ID', null=False, blank=False, default=0)

    @property
    def send_content(self):
        if self.content_id:
            from app.task.models import SendContent
            return SendContent.objects.get(id=self.content_id, user=self.customer)
        return None

    class Meta:
        managed = False
        db_table = 'track_stat'


class TrackLink(models.Model):
    """
    链接点击跟踪
    """
    id = models.AutoField(primary_key=True, db_column='link_id')
    track = models.ForeignKey(TrackStat, related_name='track_TrackStat01', null=False, blank=False, db_index=True)
    customer = models.ForeignKey(Customer, related_name='track_Customer02', null=False, blank=False)
    link = models.CharField(u'链接', null=True, blank=True, max_length=1024, db_index=True)
    click_unique = models.IntegerField(u'唯一点击数', null=False, blank=False, default=0)
    click_total = models.IntegerField(u'总点击数', null=False, blank=False, default=0)
    click_first = models.IntegerField(u'首次点击时间', null=False, blank=False, default=0)
    click_last = models.IntegerField(u'最后点击时间', null=False, blank=False, default=0)

    class Meta:
        managed = False
        db_table = 'track_link'


class StatError(models.Model):
    """
    发送失败日统计
    """
    task_id = models.IntegerField(db_index=True)
    customer = models.ForeignKey(Customer, related_name='track_Customer04', null=False, blank=False)
    send_date = models.DateField(u'日期', null=False, default='0000-00-00')
    error_type = models.SmallIntegerField(u'错误类型', default=0)
    sender = models.CharField(u'发件人', null=True, blank=True, max_length=60)
    recipient = models.CharField(u'收件人', null=True, blank=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'stat_error_list'
        index_together = ( ("customer", "send_date", "error_type") )

class StatSender(models.Model):
    """
    发送人日统计
    """
    date = models.DateField(u'日期', null=False, default='0000-00-00', db_index=True)
    customer = models.ForeignKey(Customer, related_name='track_Customer05', null=False, blank=False, db_index=True)
    sender = models.CharField(u'发件人', null=True, blank=True, max_length=60, db_index=True)
    domain = models.CharField(u'域名', null=True, blank=True, max_length=40, db_index=True)
    count = models.IntegerField(u'计数', default=0)
    lastip = models.CharField(u'使用IP', null=True, blank=True, max_length=48)

    class Meta:
        managed = False
        unique_together = (("date", "customer", "sender"),)
        db_table = 'stat_sender'

# class StatReject(models.Model):
#     pass
