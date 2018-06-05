# -*- coding: utf-8 -*-
#

import json
import datetime
from django.utils.translation import ugettext_lazy as _

from app.review.models import Department
from app.review.models import Review, ReviewRule, ReviewCondition
from app.review import constants
from lib.forms import BaseFormField, BaseFieldFormat, BaseFieldFormatExt, BaseFieldFormatOption
from lib.tools import clear_redis_cache

# 自定义 form 验证
#  审核
class ReviewForm(object):

    def __init__(self, post=None, instance=None):
        self.__instance = instance
        self.__post = post
        self.__valid = True
        self.__init()

    def is_valid(self):
        self.__check()
        return self.__valid

    def save(self):
        if self.__instance is None:
            Review.objects.create(
                name=self.name.value, next_id=self.next_id.value,
                master_review_id=self.master_review_id.value, assist_review=self.assist_review_id.value,
                wait_next_time=self.wait_next_time.value,
            )
        else:
            obj = self.__instance
            obj.name=self.name.value
            obj.next_id=self.next_id.value
            obj.master_review_id=self.master_review_id.value
            obj.assist_review=self.assist_review_id.value
            obj.wait_next_time=self.wait_next_time.value
            obj.save()

    def __check(self):
        if not self.name.value:
            self.__form.name = self.__form.name._replace(error=_(u"请输入审核名称！"))
            self.__valid = False

        if self.master_review_id.value <= 0:
            self.__form.master_review_id = self.__form.master_review_id._replace(error=_(u"请选择主审！"))
            self.__valid = False

        if ( self.master_review_id.value and self.assist_review_id.value and self.master_review_id.value == self.assist_review_id.value ):
            self.__form.assist_review_id = self.__form.assist_review_id._replace(error=_(u"主审副审不能选择相同的！"))
            self.__valid = False

        if self.wait_next_time.value < 0:
            self.__form.wait_next_time = self.__form.wait_next_time._replace(error=_(u"等待时间不能小于0！"))
            self.__valid = False

    def __init(self):
        self.__form = BaseFormField()
        if self.__post is not None:
            next_id = self.__post.get("next_id", "").strip()
            next_obj = Review.objects.filter(id=next_id and int(next_id) or 0).first()

            master_review_id = self.__post.get("master_review_id", "")
            master_review_id = master_review_id and int(master_review_id) or 0

            assist_review_id = self.__post.get("assist_review_id", "")
            assist_review_id = assist_review_id and int(assist_review_id) or 0

            wait_next_time = self.__post.get("wait_next_time", "")
            wait_next_time = wait_next_time and int(wait_next_time) or 0
            self.__form.name = BaseFieldFormat(value=self.__post.get("name", "").strip(), error=None)
            self.__form.next_id = BaseFieldFormatExt(value=next_obj and next_id or 0, error=None, extra=next_obj and next_obj.name or "")
            self.__form.master_review_id = BaseFieldFormat(value=master_review_id, error=None)
            self.__form.assist_review_id = BaseFieldFormat(value=assist_review_id, error=None)
            self.__form.wait_next_time = BaseFieldFormat(value=wait_next_time, error=None)
        else:
            if self.__instance is None:
                self.__form.name = BaseFieldFormat(value="", error=None)
                self.__form.next_id = BaseFieldFormatExt(value=0, error=None, extra="")
                self.__form.master_review_id = BaseFieldFormat(value=0, error=None)
                self.__form.assist_review_id = BaseFieldFormat(value=0, error=None)
                self.__form.wait_next_time = BaseFieldFormat(value=0, error=None)
            else:
                next_id = self.__instance.next_id
                next_obj = Review.objects.filter(id=next_id).first()
                self.__form.name = BaseFieldFormat(value=self.__instance.name, error=None)
                self.__form.next_id = BaseFieldFormatExt(value=next_obj and int(next_id) or 0, error=None, extra=next_obj and next_obj.name or "")
                self.__form.master_review_id = BaseFieldFormat(value=self.__instance.master_review_id, error=None)
                self.__form.assist_review_id = BaseFieldFormat(value=self.__instance.assist_review, error=None)
                self.__form.wait_next_time = BaseFieldFormat(value=self.__instance.wait_next_time, error=None)

    # -------- field property -------------
    name = property(fget=lambda self: self.__form.name, fset=None, fdel=None, doc=None)
    next_id = property(fget=lambda self: self.__form.next_id, fset=None, fdel=None, doc=None)
    master_review_id = property(fget=lambda self: self.__form.master_review_id, fset=None, fdel=None, doc=None)
    assist_review_id = property(fget=lambda self: self.__form.assist_review_id, fset=None, fdel=None, doc=None)
    wait_next_time = property(fget=lambda self: self.__form.wait_next_time, fset=None, fdel=None, doc=None)
    # 模型
    instance = property(fget=lambda self: self.__instance, fset=None, fdel=None, doc=None)

#  审核规则
class ReviewRuleForm(object):

    reviewrule_workmodes = constants.REVIEWRULE_WORKMODE
    reviewrule_logics = constants.REVIEWRULE_LOGIC
    reviewrule_hasattachs = constants.REVIEWRULE_HASATTACH
    reviewrule_disableds = constants.REVIEWRULE_DISABLED
    reviewrule_preactions = constants.REVIEWRULE_PREACTION

    reviewrule_option = constants.REVIEWRULE_OPTION_TYPE
    reviewrule_option_ruletypes = constants.REVIEWRULE_OPTION_TYPE_NO
    reviewrule_option_attachtypes = constants.REVIEWRULE_OPTION_TYPE_YES

    reviewrule_option_action_contains = dict(constants.REVIEWRULE_OPTION_CONDITION_CONTAIN).keys()
    reviewrule_option_condition_contains = constants.REVIEWRULE_OPTION_CONDITION_CONTAIN
    reviewrule_option_condition_eqs = constants.REVIEWRULE_OPTION_CONDITION_EQ

    def __init__(self, post=None, instance=None):
        self.__instance = instance
        self.__post = post
        self.__valid = True
        self.__init()

    def is_valid(self):
        self.__check()
        return self.__valid

    def save(self):
        if self.__instance is None:
            obj = ReviewRule.objects.create(
                review_id=self.review_id.value, name=self.name.value, workmode=self.workmode.value, cond_logic=self.cond_logic.value,
                pre_action=self.pre_action.value,sequence=self.sequence.value, disabled=self.disabled.value
            )
        else:
            obj = self.__instance
            obj.name=self.name.value
            obj.review_id=self.review_id.value
            obj.workmode=self.workmode.value
            obj.cond_logic=self.cond_logic.value
            obj.pre_action=self.pre_action.value
            obj.target_dept=self.target_dept.value
            obj.sequence=self.sequence.value
            obj.disabled=self.disabled.value
            obj.save()
        self.__saveCdt(obj.id)
        return

    def __saveCdt(self, rule_id):
        ReviewCondition.objects.filter(rule_id=rule_id).delete()
        bulks = []
        for d in self.option.value:
            if not d.value: continue
            bulks.append(
                ReviewCondition(rule_id=rule_id, option=d.type, action=d.action, value=d.value)
            )
        ReviewCondition.objects.bulk_create(bulks)

    def __check(self):
        if not self.name.value:
            self.__form.name = self.__form.name._replace(error=_(u"请填写规则名称！"))
            self.__valid = False

        if not Review.objects.filter(pk=self.review_id.value).first():
            self.__form.review_id = self.__form.review_id._replace(error=_(u"请选择审核人！"))
            self.__valid = False

    @staticmethod
    def __check_format_time(value):
        try:
            datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return True
        except:
            return False

    def __init(self):
        self.__form = BaseFormField()
        if self.__post is not None:
            review_id = self.__post.get("review_id", "").strip()
            review_obj = Review.objects.filter(id=review_id and int(review_id) or 0).first()

            target_dept = self.__post.get('target_dept', "")
            dept_obj = Department.objects.filter(pk=target_dept and int(target_dept) or -1).first()

            sequence = self.__post.get("sequence", "")
            sequence = sequence and int(sequence) or 0

            disabled = self.__post.get("disabled", "")
            disabled = disabled and int(disabled) or -1

            opts=[]
            index = 1
            opt_error = None
            option_ids = self.__post.getlist('option_ids[]', '')
            for rid in option_ids:
                error = None
                ruletype = self.__post.get('ruletype{}'.format(rid), "")
                if ruletype == "date":
                    action = self.__post.get('rule_action_eq{}'.format(rid), "")
                    value = self.__post.get('rule_value_date{}'.format(rid), "")
                    if not value or not self.__check_format_time(value):
                        error = _(u"请选择邮件时间！")
                        opt_error=True
                elif ruletype == "mail_size" or ruletype == "attach_size":
                    action = self.__post.get('rule_action_eq{}'.format(rid), "")
                    value = self.__post.get('rule_value_size{}'.format(rid), "")
                    value = value and int(value) or 0
                    if value<=0:
                        error = _(u"必须大于0！")
                        opt_error=True
                elif ruletype in ('has_attach',"all_mail"):
                    action = "=="
                    value = "1"
                else:
                    action = self.__post.get('rule_action_contain{}'.format(rid), "")
                    value = self.__post.get('rule_value_common{}'.format(rid), "")
                    if not value:
                        error = _(u"请填写审核条件内容！")
                        opt_error=True
                opts.append( BaseFieldFormatOption(id=index, type=ruletype, action=action, value=value, error=error) )
                index += 1
            if opt_error:
                self.__valid = False

            self.__form.name = BaseFieldFormat(value=self.__post.get("name", "").strip(), error=None)
            self.__form.review_id = BaseFieldFormatExt(value=review_obj and int(review_id) or 0, error=None, extra=review_obj and review_obj.name or "")
            self.__form.workmode = BaseFieldFormat(value=self.__post.get("workmode", "allsend"), error=None)
            self.__form.cond_logic = BaseFieldFormat(value=self.__post.get("cond_logic", "all"), error=None)
            self.__form.pre_action = BaseFieldFormat(value=self.__post.get("pre_action", ""), error=None)
            self.__form.target_dept = BaseFieldFormatExt(value=dept_obj and int(target_dept) or -1, error=None, extra=dept_obj and dept_obj.title or '')
            self.__form.sequence = BaseFieldFormat(value=sequence, error=None)
            self.__form.disabled = BaseFieldFormat(value=disabled, error=None)
            self.__form.option = BaseFieldFormat(value=opts, error=opt_error)
        else:
            if self.__instance is None:
                self.__form.name = BaseFieldFormat(value="", error=None)
                self.__form.review_id = BaseFieldFormatExt(value=0, error=None, extra="")
                self.__form.workmode = BaseFieldFormat(value="allsend", error=None)
                self.__form.cond_logic = BaseFieldFormat(value="all", error=None)
                self.__form.pre_action = BaseFieldFormat(value="", error=None)
                self.__form.target_dept = BaseFieldFormatExt(value=-1, error=None, extra="")
                self.__form.sequence = BaseFieldFormat(value=0, error=None)
                self.__form.disabled = BaseFieldFormat(value=-1, error=None)

                self.__form.option = BaseFieldFormat(value=[ BaseFieldFormatOption(id=0, type="subject", action="in", value="", error=None) ], error=None)
            else:
                self.__form.name = BaseFieldFormat(value=self.__instance.name, error=None)
                self.__form.review_id = BaseFieldFormatExt(value=self.__instance.review_id, error=None, extra=self.__instance and self.__instance.name or "")
                self.__form.workmode = BaseFieldFormat(value=self.__instance.workmode, error=None)
                self.__form.cond_logic = BaseFieldFormat(value=self.__instance.cond_logic, error=None)
                self.__form.pre_action = BaseFieldFormat(value=self.__instance.pre_action, error=None)
                self.__form.target_dept = BaseFieldFormatExt(value=self.__instance.target_dept, error=None, extra=self.__instance.department)
                self.__form.sequence = BaseFieldFormat(value=self.__instance.sequence, error=None)
                self.__form.disabled = BaseFieldFormat(value=self.__instance.disabled, error=None)

                self.__form.option = BaseFieldFormat(value=self.__get_condition(), error=None)

    def __get_condition(self):
        lists = ReviewCondition.objects.filter(rule=self.instance)
        if lists:
            return [ BaseFieldFormatOption(id=d.id, type=d.option, action=d.action, value=d.value or "", error=None) for d in lists ]
        return [ BaseFieldFormatOption(id=0, type="subject", action="in", value="", error=None) ]

    # -------- field property -------------
    name = property(fget=lambda self: self.__form.name, fset=None, fdel=None, doc=None)
    review_id = property(fget=lambda self: self.__form.review_id, fset=None, fdel=None, doc=None)
    workmode = property(fget=lambda self: self.__form.workmode, fset=None, fdel=None, doc=None)
    cond_logic = property(fget=lambda self: self.__form.cond_logic, fset=None, fdel=None, doc=None)
    pre_action = property(fget=lambda self: self.__form.pre_action, fset=None, fdel=None, doc=None)
    target_dept = property(fget=lambda self: self.__form.target_dept, fset=None, fdel=None, doc=None)
    sequence = property(fget=lambda self: self.__form.sequence, fset=None, fdel=None, doc=None)
    disabled = property(fget=lambda self: self.__form.disabled, fset=None, fdel=None, doc=None)
    option = property(fget=lambda self: self.__form.option, fset=None, fdel=None, doc=None)
    # 模型
    instance = property(fget=lambda self: self.__instance, fset=None, fdel=None, doc=None)

#审核开关
class ReviewConfigForm(object):

    select_result = constants.REVIEWCONFIG_RESULT_NOTIFY_OPTION
    select_notify = constants.REVIEWCONFIG_REVIEWER_NOTIFY_OPTION

    def __init__(self, post=None, instance=None, instance2=None, instance3=None):
        self.__instance = instance
        self.__instance2 = instance2
        self.__instance3 = instance3
        self.__post = post
        self.__valid = True
        self.__init()

    def is_valid(self):
        self.__check()
        return self.__valid

    def __check(self):
        if not self.value.value:
            self.__form.value = self.__form.value._replace(error=_(u"需要输入值"))
            self.__valid = False

        if not self.value_review_notify_result.value in dict(constants.REVIEWCONFIG_RESULT_NOTIFY_OPTION):
            self.__form.value_review_notify_result = self.__form.value_review_notify_result._replace(error=_(u"需要输入正确的值"))
            self.__valid = False

        if not self.value_reviewer_no_mail.value in dict(constants.REVIEWCONFIG_REVIEWER_NOTIFY_OPTION):
            self.__form.value_reviewer_no_mail = self.__form.value_reviewer_no_mail._replace(error=_(u"需要输入正确的值"))
            self.__valid = False

        return self.__valid

    def save(self):
        data_map = {
            "sw_use_review_new" : (self.__instance, self.value.value),
            "review_notify_result" : (self.__instance2, self.value_review_notify_result.value),
            "reviewer_no_mail" : (self.__instance3, self.value_reviewer_no_mail.value),
        }

        for item_name, data in data_map.iteritems():
            obj , value = data
            if obj is None:
                obj = ReviewConfig.objects.create(
                    item=item_name, co_type="system",
                    domain_id=0, value=value,
                )
            else:
                obj.domain_id=self.domain_id.value
                obj.co_type=self.co_type.value
                obj.item=item_name
                obj.value=value
                obj.save()
        clear_redis_cache()

    def __init(self):
        self.__form = BaseFormField()
        if self.__post is not None:
                value = self.__post.get("sw_new_review_value", "")
                value = "0" if value.strip()!='1' else '1'

                self.__form.domain_id = BaseFieldFormat(value=0, error=None)
                self.__form.co_type = BaseFieldFormat(value="system", error=None)

                self.__form.item = BaseFieldFormat(value="sw_use_review_new", error=None)
                self.__form.value = BaseFieldFormat(value=value, error=None)

                value_review_notify_result = self.__post.get("review_notify_result","")
                if not value_review_notify_result.strip():
                    value_review_notify_result = constants.REVIEWCONFIG_RESULT_NOTIFY_DEFAULT
                else:
                    value_review_notify_result = value_review_notify_result.strip()
                self.__form.item_review_notify_result = BaseFieldFormat(value="review_notify_result", error=None)
                self.__form.value_review_notify_result = BaseFieldFormat(value=value_review_notify_result, error=None)

                value_reviewer_no_mail = self.__post.get("reviewer_no_mail","")
                value_reviewer_no_mail = "0" if value_reviewer_no_mail.strip()!='1' else '1'
                self.__form.item_reviewer_no_mail = BaseFieldFormat(value="reviewer_no_mail", error=None)
                self.__form.value_reviewer_no_mail = BaseFieldFormat(value=value_reviewer_no_mail, error=None)
        else:
            if self.__instance is None:
                self.__form.domain_id = BaseFieldFormat(value=0, error=None)
                self.__form.co_type = BaseFieldFormat(value="system", error=None)

                self.__form.item = BaseFieldFormat(value="sw_use_review_new", error=None)
                self.__form.value = BaseFieldFormat(value="0", error=None)

            else:
                self.__form.domain_id = BaseFieldFormat(value=self.__instance.domain_id, error=None)
                self.__form.co_type = BaseFieldFormat(value=self.__instance.co_type, error=None)

                self.__form.item = BaseFieldFormat(value=self.__instance.item, error=None)
                self.__form.value = BaseFieldFormat(value=self.__instance.value, error=None)

            if self.__instance2 is None:
                self.__form.item_review_notify_result = BaseFieldFormat(value="review_notify_result", error=None)
                self.__form.value_review_notify_result = BaseFieldFormat(value=constants.REVIEWCONFIG_RESULT_NOTIFY_DEFAULT, error=None)
            else:
                self.__form.item_review_notify_result = BaseFieldFormat(value=self.__instance2.item, error=None)
                self.__form.value_review_notify_result = BaseFieldFormat(value=self.__instance2.value, error=None)

            if self.__instance3 is None:
                self.__form.item_reviewer_no_mail = BaseFieldFormat(value="reviewer_no_mail", error=None)
                self.__form.value_reviewer_no_mail = BaseFieldFormat(value='0', error=None)
            else:
                self.__form.item_reviewer_no_mail = BaseFieldFormat(value=self.__instance3.item, error=None)
                self.__form.value_reviewer_no_mail = BaseFieldFormat(value=self.__instance3.value, error=None)

    domain_id = property(fget=lambda self: self.__form.domain_id, fset=None, fdel=None, doc=None)
    co_type = property(fget=lambda self: self.__form.co_type, fset=None, fdel=None, doc=None)

    item = property(fget=lambda self: self.__form.item, fset=None, fdel=None, doc=None)
    value = property(fget=lambda self: self.__form.value, fset=None, fdel=None, doc=None)

    item_review_notify_result = property(fget=lambda self: self.__form.item_review_notify_result, fset=None, fdel=None, doc=None)
    value_review_notify_result = property(fget=lambda self: self.__form.value_review_notify_result, fset=None, fdel=None, doc=None)

    item_reviewer_no_mail = property(fget=lambda self: self.__form.item_reviewer_no_mail, fset=None, fdel=None, doc=None)
    value_reviewer_no_mail = property(fget=lambda self: self.__form.value_reviewer_no_mail, fset=None, fdel=None, doc=None)

    # 模型
    instance = property(fget=lambda self: self.__instance, fset=None, fdel=None, doc=None)
    instance2 = property(fget=lambda self: self.__instance2, fset=None, fdel=None, doc=None)
    instance3 = property(fget=lambda self: self.__instance3, fset=None, fdel=None, doc=None)
