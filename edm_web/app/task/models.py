# coding=utf-8
from __future__ import unicode_literals

import json
import datetime
import hashlib
import urllib2

from django.db import models
from django.db.models import Sum
from app.core.models import Customer
from app.template.models import SendTemplate
from django.conf import settings
from app.track.models import StatTask, TrackStat, TrackLink
from lib.tools import ZeroDateTimeField
from django_redis import get_redis_connection

from app.template.templatetags.template_tags import filesizeformat

from django.utils.translation import ugettext_lazy as _

SEND_ACCT_TYPE = (
    ('all', _(u'所有域名')),
    ('domain', _(u'单个域名')),
)

SEND_STATUS = (
    (-5, _(u'等待入库启动')),
    (-4, _(u'发送出错')),
    (-3, _(u'取消发送')),
    (-2, _(u'暂停发送')),
    (-1, _(u'暂不发送')),
    # (0, u'等待发送'),
    (1, _(u'等待启动')),
    (2, _(u'正在发送')),
    (3, _(u'发送完成')),
    (4, _(u'任务停止')),
)

VERIFY_STATUS = (
    (0, _(u'等待审核')),
    (1, _(u'审核通过')),
    (2, _(u'审核拒绝')),
)

TRACK_STATUS = (
    (0, _(u'不跟踪')),
    (1, _(u'跟踪邮件打开情况')),
    (2, _(u'跟踪邮件打开与链接点击情况')),
)
HOUR_SPEED = (
    (0, _(u"请选择")),
    (500, _(u"500")),
    (1000, _(u"1000")),
    (5000, _(u"5000")),
    (10000, _(u"10000")),
    (25000, _(u"25000")),
    (50000, _(u"50000")),
    (75000, _(u"75000")),
)

EDM_TASK = ":umailweb:task:" # {"sendname": sendname, "user_id": 2369, "task_id": 1, "action": "run" or "stop"}

class SendTaskReplyto(models.Model):
    """
    指定恢复地址
    建立任务的时候，如果客户输入“指定回复地址”，则记住这个地址，下次客户建立任务的时候自动填入，直到客户修改或删除这个
    """
    user = models.ForeignKey(Customer, related_name='send_task_replyto', null=False, blank=False, db_index=True)
    send_replyto = models.CharField(u'指定回复地址', null=True, blank=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'ms_send_replyto'

class SendTask(models.Model):
    """
    任务类
    """
    id = models.AutoField(primary_key=True, db_column='send_id')
    user = models.ForeignKey(Customer, related_name='task_Customer', null=False, blank=False)
    send_name = models.CharField(u'任务名称', null=True, blank=True, max_length=64)
    send_acct_type = models.CharField(u'发送账号类型', null=True, blank=True, max_length=10, default='all',
                                      choices=SEND_ACCT_TYPE)
    send_acct_domain = models.CharField(u'发送账号域名', null=True, blank=True, max_length=60, default='all')

    send_acct_address = models.CharField(u'发送地址', null=True, blank=True, max_length=70)
    send_account = models.CharField(u'发送账号', null=True, blank=True, max_length=50)

    send_replyto = models.CharField(u'指定回复地址', null=True, blank=True, max_length=50)
    send_fullname = models.CharField(u'发送人名称', null=True, blank=True, max_length=50)

    send_template = models.CharField(u'模板名称', null=True, blank=True, max_length=100)
    send_template_id = models.IntegerField(u'模板ID', null=True, blank=True, default=0)
    # send_addr_type、send_category、send_category_id

    send_maillist = models.CharField(u'发送邮件列表名', null=True, blank=True, max_length=100)
    send_maillist_id = models.IntegerField(u'发送邮件列表名ID', null=True, blank=True)

    # send_shared、send_shared_id
    send_qty_start = models.IntegerField(u'发送开始数量', null=False, blank=False, default=0)
    send_qty = models.IntegerField(u'发送列表邮箱数量', null=False, blank=False, default=0)
    send_qty_remark = models.IntegerField(u'发送列表邮箱数量', null=False, blank=False, default=0)
    send_time = ZeroDateTimeField(u'任务发送时间', null=True)
    send_status = models.SmallIntegerField(u'任务状态', default=0, choices=SEND_STATUS)
    verify_status = models.SmallIntegerField(u'审核状态', default=1, choices=VERIFY_STATUS)
    send_count = models.IntegerField(u'成功发送数', null=False, blank=False, default=0)
    error_count = models.IntegerField(u'发送失败数', null=False, blank=False, default=0)
    time_start = ZeroDateTimeField(u'任务开始时间', null=True, blank=True)
    time_end = ZeroDateTimeField(u'任务结束时间', null=True, blank=True)
    track_status = models.SmallIntegerField(u'跟踪状态', default=0, choices=TRACK_STATUS)
    track_domain = models.CharField(u'客户指定域名', null=True, blank=True, max_length=100, help_text=u'客户指定域名，替换跟踪统计链接域名')
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(u'修改时间', null=True, auto_now=True)
    isvalid = models.BooleanField(u'是否有效', default=True)
    is_new = models.BooleanField(u'是否是新平台创建的', default=True)
    is_need_receipt = models.BooleanField(u'邮件阅读回执', default=0)
    # is_api = models.BooleanField(u'是否是通过API创建的任务', default=False)
    is_shield = models.BooleanField(_(u'是否被屏蔽'), default=False)
    # 发送速度, 每小时发送速度
    hour_speed = models.IntegerField(_(u"发送速度"), default=0, choices=HOUR_SPEED, help_text=u"单位：小时，每小时最大发送量")
    # A/B发送
    is_ab = models.BooleanField(u"A/B发送", default=False)
    ab_appraise_qty = models.IntegerField(u"评估数量", default=0)
    ab_content_limit = models.IntegerField(u"模板限制数量", default=0)
    # """
    # ALTER TABLE `ms_send_list` ADD `is_ab` TINYINT( 1 ) NOT NULL DEFAULT '0' COMMENT 'AB发送',
    #     ADD `ab_appraise_qty` INT( 11 ) NOT NULL DEFAULT '0' COMMENT '评估数量',
    #     ADD `ab_content_limit` INT( 11 ) NOT NULL DEFAULT '0' COMMENT '模板限制数量';
    # """

    def __unicode__(self):
        return self.send_name

    class Meta:
        managed = False
        db_table = 'ms_send_list'

    def get_real_send_qty(self):
        """
        获取真实发送数量
        """
        return int(self.send_qty) - int(self.send_qty_start) + 1 if self.send_qty else int(self.send_qty_remark)

    def start(self):
        self.redis_operate('run')
        # if self.user_id == 2369:
        #     self.redis_operate('run')
        # else:
        #     self.operate('start')

    def stop(self):
        self.redis_operate('stop')
        # if self.user_id == 2369:
        #     self.redis_operate('stop')
        # else:
        #     self.operate('stop')

    def redis_operate(self, action):
        # EDM_TASK = "f2df4350-059b-11e8-921a-005056a7d988:edm:web:task:"   # {"sendname": sendname, "user_id": 2369, "task_id": 1, "action": "run" or "stop"}
        redis = get_redis_connection()
        redis.lpush(EDM_TASK, json.dumps({
            "sendname": self.send_name,
            "user_id": self.user_id,
            "task_id": self.id,
            "action": action,
        }))

    def operate(self, op):
        url = 'http://{host}:{port}/new_task?&act={op}&uid={uid}&tid={tid}&auth={auth}'.format(**{
            'host': settings.WEB_API_HOST,
            'port': settings.WEB_API_PORT,
            'op': op,
            'uid': self.user.id,
            'tid': self.id,
            'auth': hashlib.md5('%s-%s' % (settings.WEB_API_AUTH_KEY, datetime.datetime.now().strftime("%Y%m%d"))).hexdigest()
        })
        try:
            urllib2.urlopen(url)
        except:
            pass


    def get_send_rate(self):
        # send_total_tmp = self.send_qty if self.send_qty else self.send_qty_remark
        send_total_tmp = self.get_real_send_qty()
        if self.send_status in [2, -2, 3, -3, 4, -4]:
            if self.send_status == 3:
                stat_send = StatTask.objects.filter(task_ident=self.send_name).aggregate(count_send=Sum('count_send'))['count_send']
                rate = float(stat_send) / float(self.send_count) if self.send_count and stat_send else 0
            else:
                rate = float(self.send_count) / float(send_total_tmp) if send_total_tmp else 0

            rate = rate if rate < 0.98 else 1
            return '%.2f%s' % (rate * 100, '%')
        return 0

    def get_track_stat_flag(self):
        if TrackStat.objects.filter(task_ident=self.send_name, customer_id=self.user.id).exists():
            return True
        return False

    def get_stat_obj(self):
        try:
            stat_objs = TrackStat.objects.filter(task_ident=self.send_name, customer_id=self.user.id)
            stat_obj = stat_objs[0]
        except:
            stat_obj = None
        return stat_obj

    def get_rate(self):
        value = StatTask.objects.filter(task_ident=self.send_name, customer_id=self.user.id).aggregate(count_send=Sum('count_send'), count_error=Sum('count_error'))
        track_value = TrackStat.objects.filter(task_ident=self.send_name, customer=self.user)\
            .aggregate(open_unique=Sum('open_unique'), click_unique=Sum('click_unique'))
        count_send = value['count_send'] if value['count_send'] else 0
        count_error = value['count_error'] if value['count_error'] else 0
        count_succes = count_send - count_error

        open_unique = track_value['open_unique'] if track_value['open_unique'] else 0
        click_unique = track_value['click_unique'] if track_value['click_unique'] else 0
        show_stat_rate = self._get_rate(open_unique, count_succes)
        show_link_rate = self._get_rate(click_unique, open_unique)
        return show_stat_rate, show_link_rate

    def _get_rate(self, unique, total):
        if total:
            return "{}%".format(round( ( int(unique)*100.00/int(total) ), 2) )
        return '0%'

    def show_template_list(self):
        lists = SendContent.objects.filter(send=self, isvalid=True)
        count = 1
        html = u''
        for obj in lists:
            size = int(obj.size)
            if size:
                html = html + _(u"""<p><strong class="margin-right-5">%(count)d.</strong>
                            <a type="button" href="/task/preview/%(task_id)d/" target="_blank" class="margin-right-5">%(template_name)s</a>
                            <span class="text-muted">(大约：%(size)s)</span>
                            </p>""") % {
                    'count': count,
                    'task_id': int(obj.id),
                    'template_name': obj.template_name,
                    'size': filesizeformat(size),
                }
            elif obj.template_name:
                html = html + _(u"""<p><strong class="margin-right-5">%(count)d.</strong>
                            <a type="button" href="/task/preview/%(task_id)d/" target="_blank" class="margin-right-5">%(template_name)s</a>
                            <span class="text-muted">(大约：%(size)s)</span>
                            </p>""") % {
                    'count': count,
                    'task_id': int(obj.id),
                    'template_name': obj.template_name,
                    'size': filesizeformat(len(obj.send_content)),
                }
            else:
                template_name = obj.send.send_template if obj.send.send_template else _('未命名模板')
                html = html + _(u"""<p><strong class="margin-right-5">%(count)d.</strong>
                            <a type="button" href="/task/preview/%(task_id)d/" target="_blank" class="margin-right-5">%(template_name)s</a>
                            <span class="text-muted">(大约：%(size)s)</span>
                            </p>""") % {
                    'count': count,
                    'task_id': int(obj.id),
                    'template_name': template_name,
                    'size': filesizeformat(len(obj.send_content)),
                }
            count += 1
        return html

    def get_copy_template_ids(self):
        lists = SendContent.objects.filter(send=self)
        template_ids = [obj.template_id for obj in lists if int(obj.template_id)]
        return template_ids if template_ids else [self.send_template_id]

    def get_verify_log(self):
        """
        获取任务审核拒绝的原因
        """
        if self.verify_status == 2:
            return SendVerifyLog.objects.filter(send=self.pk).order_by('-created').first().memo
        return ''

    def get_count_error_5(self):
        value = StatTask.objects.filter(task_ident=self.send_name).aggregate(count_err_5=Sum('count_err_5'))
        count_err_5 = int(value['count_err_5']) if value['count_err_5'] else 0
        return count_err_5

    def show_stat_success_info(self):
        send_total = self.get_real_send_qty()

        # 取得任务实际发送量
        value = StatTask.objects.filter(customer_id=self.user.id, task_ident=self.send_name).aggregate(
            count_send=Sum('count_send'), count_error=Sum('count_error'),
            count_err_1=Sum('count_err_1'), count_err_2=Sum('count_err_2'),
            count_err_3=Sum('count_err_3'), count_err_5=Sum('count_err_5'),
        )
        count_send = value['count_send'] if value['count_send'] else 0
        count_error = int(value['count_error']) if value['count_error'] else 0  # 发送失败
        count_succes = count_send - count_error  # 发送成功
        # 格式错误、无效
        count_invalid = send_total - count_send
        # 邮箱不存在
        count_err_1 = value['count_err_1'] if value['count_err_1'] else 0
        # 空间不足
        count_err_2 = value['count_err_2'] if value['count_err_2'] else 0
        # 用户拒收
        count_err_3 = value['count_err_3'] if value['count_err_3'] else 0
        # 垃圾拒绝发送
        count_err_5 = value['count_err_5'] if value['count_err_5'] else 0

        # 全部送达率和真实发送送达率
        all_send_rate = self._get_rate(count_succes, send_total)
        success_send_rate = self._get_rate(count_succes, count_send - count_err_5)

        # 失败地址总数：
        total_error = count_invalid + count_err_1 + count_err_2 + count_err_3 + count_err_5

        return _(u'''
        <span class="text-nowrap">%(all_send)s：
            <span class="myself-txt-color-red">%(rate)s</span>
        </span><br>
        <span class="text-nowrap">%(all_real_send)s：
            <span class="myself-txt-color-red">%(send_rate)s</span>
        </span><br>
        <span class="text-nowrap">%(fail_send)s：
            <span class="myself-txt-color-blue margin-right-5">%(error)d</span>
        </span><br>
        <span class="text-nowrap">
            <code><a href="/statistics/report/%(task_id)d/" target="_blank">%(view_detail)s</a></code>
        </span>
        ''') % {'rate': all_send_rate, 'send_rate': success_send_rate, 'error': total_error, 'task_id': int(self.id),
                'all_send': _(u"全部送达率"), 'all_real_send': _(u"真实发送送达率"), 'fail_send': _(u"失败地址数量"),
                'view_detail': _(u"查看统计详情"),
                }


class SendTaskTpl(models.Model):
    """
    任务模板类　一个任务可以有多个模板
    """
    task = models.ForeignKey(SendTask, related_name='taskSendTask01', null=False, blank=False)
    template = models.ForeignKey(SendTemplate, related_name='taskSendTemplate01', null=False, blank=False,
                                 db_index=True)
    send_count = models.IntegerField(u'发送数量', default=0)
    send_success = models.IntegerField(u'成功数量', default=0)

    class Meta:
        managed = False
        db_table = 'ms_send_list_tpl'


class SendContent(models.Model):
    """
    任务 邮件模板
    """
    send = models.ForeignKey(SendTask, related_name='taskSendTask02', null=False, blank=False)
    template = models.ForeignKey(SendTemplate, related_name='taskSendTemplate02', null=False, blank=False)
    template_name = models.CharField(u'模板名称', null=True, blank=True, max_length=100)
    user = models.ForeignKey(Customer, related_name='task_Customer02', null=False, blank=False)
    send_content = models.TextField(u'邮件')
    size = models.IntegerField(u'邮件大小', default=0)
    isvalid = models.BooleanField(u'是否有效', default=True)

    class Meta:
        managed = False
        db_table = 'ms_send_content'

class SendVerifyLog(models.Model):
    """
    任务审核日志
    """
    send = models.ForeignKey(SendTask, related_name='taskVerifyLog', null=False, blank=False)
    customer = models.ForeignKey(Customer, related_name='customerVerifyLog', null=False, blank=False)
    verify_status = models.SmallIntegerField(u'审核状态', default=1, choices=VERIFY_STATUS)
    memo = models.TextField()
    created = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'ms_send_verify_log'

