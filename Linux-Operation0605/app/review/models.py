# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals

import json
from django.db import models

from app.review import constants
from app.core.models import Mailbox, Department

class Review(models.Model):
    """
    主审、副审、下一级审核人
    """
    name = models.CharField(u'审核人', max_length=250, null=False, blank=True)
    # next = models.ForeignKey('self', null=True, blank=True, db_index=True, help_text=u'下一级审核')
    next_id = models.IntegerField(u'下一级审核', default=0)
    master_review = models.ForeignKey(Mailbox, related_name='master_review', db_column='master_review', on_delete=models.SET_NULL, db_index=True, null=True, blank=True)
    assist_review = models.IntegerField(u'副审', default=0, db_column='assist_review')
    wait_next_time = models.IntegerField(u'自动转换等待时间', default=0, help_text='自动把副审转换为审核人的等待时间，单位为分钟，=0为永不转移')

    class Meta:
        managed = False
        db_table = 'ext_review_new'

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        super(Review, self).delete(using=using, keep_parents=keep_parents)

    def foundWithoutEcludeIDs(self):
        exclude_ids=set()
        exclude_ids.add(self.id)
        parent_objs = Review.objects.filter(next_id=self.pk)
        Review.loopParentFoundRootID(parent_objs, exclude_ids)
        return Review.objects.exclude(id__in=exclude_ids)

    @staticmethod
    def check_master_review(obj):
        try:
            return obj.master_review
        except:
            return ""

    @staticmethod
    def check_assist_review(obj):
        try:
            if obj.assist_review <=0:
                return ""
            obj = Mailbox.objects.filter(id=obj.assist_review).first()
            return obj if obj else ""
        except Exception,err:
            return "None"

    @staticmethod
    def loopParentFoundRootID(parent_objs, exclude_ids):
        if not parent_objs:
            return exclude_ids
        for obj in parent_objs:
            exclude_ids.add(obj.id)
            parent_objs = Review.objects.filter(next_id=obj.pk)
            Review.loopParentFoundRootID(parent_objs, exclude_ids)
        return exclude_ids


    @staticmethod
    def getReviewList():
        lists = []
        next_ids = Review.objects.filter(next_id__gt=0).values_list('next_id', flat=True)
        firstReviewLists = Review.objects.exclude(id__in=next_ids)
        for obj in firstReviewLists:
            level = 0
            pk = '{}'.format(obj.id)
            lists.append(
                # id, pid, level, name, master, assist, wait_time, real_id
                ( pk, '0', level, obj.name, Review.check_master_review(obj), Review.check_assist_review(obj), obj.wait_next_time, obj.id),
            )
            Review.loopChildLists(obj, obj.id, pk, level, lists)
        return lists

    @staticmethod
    def loopChildLists(obj, id, pid, level=0, lists=None):
        next_pk = obj.next_id
        next_obj = Review.objects.filter(pk=next_pk).first()
        if not next_obj:
            return lists
        level += 1
        pk = '{}_{}'.format(pid, next_pk)
        lists.append(
            # id, pid, level, name, master, assist, wait_time, real_id
            (pk, pid, level, next_obj.name, Review.check_master_review(next_obj), Review.check_assist_review(next_obj), next_obj.wait_next_time, next_pk)
        )
        return Review.loopChildLists(next_obj, next_pk, pk, level, lists)


class ReviewRule(models.Model):
    """
    审核规则表
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE, db_index=True, null=False, blank=False)
    name = models.CharField(u'规则名称', max_length=250, null=False, blank=True)
    workmode = models.CharField(u'审核类型', max_length=20, choices=constants.REVIEWRULE_WORKMODE, default='outbount')
    cond_logic = models.CharField(u'逻辑条件', max_length=20, choices=constants.REVIEWRULE_LOGIC, default='all')
    pre_action = models.CharField(u'审核预设', max_length=20, null=True, blank=True, choices=constants.REVIEWRULE_PREACTION)
    target_dept = models.IntegerField(u'发信人部门', default=0, help_text=u'需要审核的部门ID')
    sequence = models.IntegerField(u'权重', default=999, help_text=u'数值越小优先级越高,数值相等时主键越小优先级越高')
    disabled = models.IntegerField(u'状态', default=-1, choices=constants.REVIEWRULE_DISABLED)

    class Meta:
        managed = False
        db_table = 'ext_review_new_rule'

    def __str__(self):
        return self.name

    @property
    def department(self):
        obj = Department.objects.filter(pk=self.target_dept).first()
        return obj and obj.title or ''

    def getConditionList(self):
        lists = []
        rule_list = ReviewCondition.objects.filter(rule=self)
        options = dict(constants.REVIEWRULE_OPTION_TYPE)
        actions = dict(constants.REVIEWRULE_OPTION_CONDITION)
        for obj in rule_list:
            lists.append(
                ( options.get(obj.option, ''), actions.get(obj.action, ''), obj.value )
            )
        return lists

    def getNoInputOptionList(self):
        return dict(constants.REVIEWRULE_OPTION_NO_INPUT).values()

class ReviewCondition(models.Model):

    rule = models.ForeignKey(ReviewRule, on_delete=models.CASCADE, db_index=True, null=False, blank=False)
    option = models.CharField(u'条件', max_length=50, null=True, blank=True)
    action = models.CharField(u'匹配动作', max_length=20, null=True, blank=True)
    value = models.CharField(u'参数', max_length=250, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'ext_review_new_condition'


class ReviewMail(models.Model):
    """
    原审核邮件存放表
    """
    subject = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'ext_review_mail'


class ReviewProcess(models.Model):
    """
    审核进度表，表明当前某个邮件现在是给谁在审核
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE, db_index=True, null=False, blank=False, db_column='review_id')
    mail = models.ForeignKey(ReviewMail, on_delete=models.CASCADE, null=True, blank=True, db_column='mail_id')
    reviewer = models.ForeignKey(Mailbox, on_delete=models.CASCADE, null=True, blank=True, db_column='reviewer_id')
    status = models.CharField(max_length=20, default='wait', choices=constants.REVIEWPROCESS_STATUS)
    start_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    last_update = models.DateTimeField(u'更新时间', auto_now=True)

    class Meta:
        managed = False
        db_table = 'ext_review_new_process'
        unique_together = (('review', "mail"),)


class ReviewConfig(models.Model):
    """
    服务器综合设置表
    """
    domain_id = models.IntegerField(u'域名ID', default=0, help_text=u'域名ID',db_column='domain_id')
    co_type = models.CharField(max_length=20, blank=True, db_column='type')
    item = models.CharField(max_length=35, blank=True, db_column='item')
    value = models.TextField(null=True, blank=True, db_column='value')

    class Meta:
        managed = False
        db_table = 'core_domain_attr'
        unique_together = (
            ('domain_id', 'co_type','item')
        )

    @staticmethod
    def use_review_new():
        obj = ReviewConfig.objects.filter(item="sw_use_review_new",co_type="system",domain_id=0).first()
        if not obj:
            obj = ReviewConfig.objects.create(
                item="sw_use_review_new", co_type="system",
                domain_id=0, value='0',
            )
        return obj

    @staticmethod
    def result_notify_option():
        obj = ReviewConfig.objects.filter(item="review_notify_result",co_type="system",domain_id=0).first()
        if not obj:
            obj = ReviewConfig.objects.create(
                item="review_notify_result",
                co_type="system",
                domain_id=0,
                value=constants.REVIEWCONFIG_RESULT_NOTIFY_DEFAULT,
            )
        return obj

    @staticmethod
    def reviewer_notify_option():
        obj = ReviewConfig.objects.filter(item="reviewer_no_mail",co_type="system",domain_id=0).first()
        if not obj:
            obj = ReviewConfig.objects.create(
                item="reviewer_no_mail",
                co_type="system",
                domain_id=0,
                value=constants.REVIEWCONFIG_REVIEWER_NOTIFY_DEFAULT,
            )
        return obj
