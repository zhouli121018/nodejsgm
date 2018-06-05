# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import models
from django.template import Template, Context
from app.setting import constants
from app.core.models import Department
from lib.formats import dict_compatibility, safe_format

class ExtCfilterRuleNew(models.Model):
    """ 新的内容过滤器规则表 """
    mailbox_id = models.IntegerField(u"邮箱ID", default=0, db_index=True, null=False, blank=False,
                                     help_text=u"mailbox_id=0时为系统过滤，有值时为用户过滤")
    name = models.CharField(u"规则名称", max_length=150, null=True, blank=True, help_text=u"管理员输入的规则备注，可不填")
    type = models.IntegerField(u"类型", choices=constants.FILTER_RULE, default=-1, null=False, blank=False)
    logic = models.CharField(u"条件关系", max_length=50, default="all", choices=constants.RULE_LOGIC, null=False, blank=False,
                             help_text=u"all：满足所有条件，one：满足一条即可")
    sequence = models.IntegerField(u"规则优先级", default=999, null=False, blank=False)
    disabled = models.IntegerField(u'状态', choices=constants.DISABLED_STATUS, default=-1, null=False, blank=False)

    class Meta:
        db_table = "ext_cfilter_rule_new"
        managed = False

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        self.deleteOptions()
        self.deleteActions()
        super(ExtCfilterRuleNew, self).delete(using, keep_parents)

    def deleteOptions(self):
        ExtCfilterNewCond.objects.filter(rule_id=self.id).delete()

    def deleteActions(self):
        ExtCfilterNewAction.objects.filter(rule_id=self.id).delete()


    def getActions(self):
        return ExtCfilterNewAction.objects.filter(rule_id=self.id).order_by("sequence")

    def getOptions(self, parent_id=0):
        return ExtCfilterNewCond.objects.filter(rule_id=self.id, parent_id=parent_id)


class ExtCfilterNewCond(models.Model):
    """ 条件组表 """
    rule_id = models.IntegerField(u"所属规则", default=0, db_index=True, null=False, blank=False,
                                  help_text=u"所属节点，ext_cfilter_rule_new的主键")
    parent_id = models.IntegerField(u"父ID", db_index=True, default=0, null=False, blank=False, help_text=u"这个条件的父亲ID，逻辑关系由parent_id指向的那一行决定")
    logic = models.CharField(u"逻辑表达式", max_length=50, choices=constants.COND_LOGIC, default="all", null=False, blank=False, help_text=u"all:并且,one：或")
    option = models.CharField(u"条件1", max_length=50, null=False, blank=False, choices=constants.ALL_CONDITION_OPTION)
    suboption = models.CharField(u"条件2", max_length=50, null=False, blank=False)
    # suboption = models.CharField(u"条件2", max_length=50, null=False, blank=False, choices=constants.ALL_CONDITION_SUBOPTION)
    action = models.CharField(u"动作", max_length=50, null=False, blank=False, choices=constants.ALL_CONDITION_ACTION)
    value = models.CharField(u"值", max_length=500, null=True, blank=True)

    class Meta:
        db_table = "ext_cfilter_new_cond"
        managed = False

    def view_html(self):
        load_html = self.template_string
        t = Template(load_html)
        htmls = [ t.render(Context( {"obj": self, "parent": True} )) ]
        for d in self.Children:
            htmls.append(
                t.render(Context( {"obj": d, "parent": False} ))
            )
        return "".join(htmls)

    @property
    def template_string(self):
        return u"""
        <div class="col-sm-12">
            {% if parent %}
                <input class="col-xs-2 col-sm-2" value="{{ obj.get_logic_display }}" disabled/>
            {% else %}
                <label class="col-xs-2 col-sm-2"></label>
            {% endif %}
            <input class="col-xs-2 col-sm-2" value="{{ obj.suboption_display }}" disabled/>
            <input class="col-xs-2 col-sm-2" value="{{ obj.get_action_display }}" disabled/>
            <input class="col-xs-4 col-sm-4" value="{{ obj.value_display }}" disabled/>
        </div>
        """

    @property
    def Children(self):
        return ExtCfilterNewCond.objects.filter(parent_id=self.id)

    @property
    def suboption_display(self):
        if self.option in ("header", "extra"):
            d = dict(constants.ALL_CONDITION_SUBOPTION)
            if self.suboption in d:
                return d[self.suboption]
        return self.suboption

    @property
    def value_display(self):
        d = dict(constants.ALL_CONDITION_SUBOPTION)
        if self.option in ("header", "extra"):
            if self.suboption in constants.G_COND_OPTION_IN:
                try:
                    value = int(self.value)
                except:
                    value = 0
                obj = Department.objects.filter(id=value).first()
                return obj and obj.title or ""
            elif self.suboption in constants.G_COND_OPTION_GTE:
                try:
                    value = int(self.value)
                except:
                    value = 0
                return u"{}M".format(value)
            elif self.suboption in constants.G_COND_OPTION_EQ:
                if self.value == "1":
                    return u'是'
                else:
                    return u'否'
            elif self.suboption in constants.G_COND_OPTION_OTHER:
                return self.value
            else:
                return self.value
        return ""

class ExtCfilterNewAction(models.Model):
    """ 新的内容过滤器动作表 """
    rule_id = models.IntegerField(u"所属规则", default=0, db_index=True, null=False, blank=False,
                                  help_text=u"所属节点，ext_cfilter_rule_new的主键")
    action = models.CharField(u"动作", max_length=50, null=False, blank=False, choices=constants.ALL_ACTION)
    value = models.CharField(u"值", max_length=500, null=True, blank=True)
    sequence = models.IntegerField(u"动作优先级", default=999, null=False, blank=False)

    class Meta:
        db_table = "ext_cfilter_new_action"
        managed = False

    def view_html(self):
        T = '<div class="col-sm-12"><div class="hr hr-6 hr-dotted"></div></div>'
        load_html = self.template_string
        htmls = [ safe_format(load_html, **{ "name": u"动作", "value": self.get_action_display() }) ]
        htmls.append(T)
        htmls.append( safe_format(load_html, **{ "name": u"优先级", "value": self.sequence }) )

        j = self.json_value
        # if self.action in ("break", "flag", "label", "delete", "sequester"):
        #     pass
        if self.action in ("move_to", "copy_to"):
            d = dict(constants.CFILTER_ACTION_SELECT_VALUE)
            value = ""
            key = dict_compatibility(j, "value")
            if key in d:  value = d[key]
            htmls.append(T)
            htmls.append( safe_format(load_html, **{ "name": u"设置值", "value":  value }) )

        if self.action in ("jump_to", "forward", "delete_header", "append_body"):
            value = dict_compatibility(j, "value")
            htmls.append(T)
            htmls.append( safe_format(load_html, **{ "name": u"设置值", "value":  value }) )

        if self.action in ("append_header", ):
            field = dict_compatibility(j, "field")
            value = dict_compatibility(j, "value")
            htmls.append(T)
            htmls.append( safe_format(load_html, **{ "name": u"邮件头", "value":  field }) )
            htmls.append( safe_format(load_html, **{ "name": u"邮件头设置值", "value":  value }) )

        if self.action in ("mail", ):
            mail_sender = dict_compatibility(j, "sender")
            mail_recipient = dict_compatibility(j, "recipient")
            mail_subject = dict_compatibility(j, "subject")
            mail_type = dict_compatibility(j, "content_type")
            content = dict_compatibility(j, "content")
            if mail_type == "html":
                mail_type = "html内容"
            else:
                mail_type = "纯文本"
            htmls.append(T)
            htmls.append( safe_format(load_html, **{ "name": u"发信人", "value":  mail_sender }) )
            htmls.append( safe_format(load_html, **{ "name": u"收信人", "value":  mail_recipient }) )
            htmls.append( safe_format(load_html, **{ "name": u"主题", "value":  mail_subject }) )
            htmls.append( safe_format(load_html, **{ "name": u"类型", "value":  mail_type }) )
            htmls.append( safe_format(load_html, **{ "name": u"内容", "value":  content }) )

        if self.action in ("smtptransfer", ):
            trans_server = dict_compatibility(j, "server")
            trans_account = dict_compatibility(j, "account")
            trans_ssl = dict_compatibility(j, "ssl")
            trans_auth = dict_compatibility(j, "auth")
            htmls.append(T)
            htmls.append( safe_format(load_html, **{ "name": u"SMTP服务器", "value":  trans_server }) )
            htmls.append( safe_format(load_html, **{ "name": u"登录帐号", "value":  trans_account }) )
            htmls.append( safe_format(load_html, **{ "name": u"需要验证", "value":  trans_auth }) )
            htmls.append( safe_format(load_html, **{ "name": u"SSL登录", "value":  trans_ssl }) )

        return "".join(htmls)

    @property
    def template_string(self):
        return u"""<div class="col-sm-12"><label class="col-xs-2 col-sm-2">{name}：</label><label class="col-xs-10 col-sm-10 ">{value}</label></div>"""

    @property
    def json_value(self):
        try:
            return json.loads(self.value)
        except:
            return {}

# ext_account_transfer
class AccountTransfer(models.Model):

    mailbox_id = models.IntegerField(u"MailBox", default=0)
    mailbox = models.CharField(u"离职帐号", max_length=200, null=True, blank=True)
    mailbox_to = models.CharField(u"目标帐号", max_length=200, null=True, blank=True)
    mode = models.CharField(u"迁移模式", max_length=200, null=True, blank=True)
    succ_del = models.IntegerField(u'删除帐号', choices=constants.ACCOUNT_TRANSFER_DEL, null=False, blank=False, default="-1")
    status = models.CharField(u'状态', max_length=20, choices=constants.ACCOUNT_TRANSFER_STATUS, null=False, blank=False, default="-1")
    desc_msg = models.TextField(u"状态描述", null=True, blank=True)
    last_update = models.DateTimeField(u"状态更新时间", null=False, blank=False)
    disabled = models.CharField(u'开始迁移', max_length=2, choices=constants.ACCOUNT_TRANSFER_DISABLE, null=False, blank=False, default="-1")

    class Meta:
        managed = False
        db_table = 'ext_account_transfer'

# ext_imapmail
class IMAPMoving(models.Model):

    mailbox_id = models.IntegerField(u"MailBox", default=0)
    mailbox = models.CharField(u"本地帐号", max_length=200, null=False, blank=True)
    src_mailbox = models.CharField(u"远程帐号", max_length=200, null=True, blank=True)
    src_server = models.CharField(u"远程服务器", max_length=200, null=True, blank=True)
    ssl = models.CharField(u'SSL访问', max_length=2, choices=constants.ACCOUNT_IMAPMOVING_SSL, null=False, blank=False, default="-1")
    src_folder = models.CharField(u'迁移目录', max_length=100, choices=constants.ACCOUNT_IMAPMOVING_FOLDER, null=False, blank=False, default="all")
    src_password = models.CharField(u"密码", max_length=200, null=True, blank=True)
    set_from = models.CharField(u'来源', max_length=20, choices=constants.ACCOUNT_IMAPMOVING_SETFROM, null=False, blank=False, default="-1")
    status = models.CharField(u'状态', max_length=20, choices=constants.ACCOUNT_IMAPMOVING_STATUS, null=False, blank=False, default="-1")
    desc_msg = models.TextField(u"状态描述", null=True, blank=True)
    last_update = models.DateTimeField(u"状态更新时间", null=False, blank=False)
    disabled = models.CharField(u'激活状态', max_length=2, choices=constants.ACCOUNT_IMAPMOVING_DISABLE, null=False, blank=False, default="-1")

    class Meta:
        managed = False
        db_table = 'ext_imapmail'

# ext_popmail
class POP3Moving(models.Model):

    domain_id = models.IntegerField(u"域名ID", default=0, db_index=True, null=False, blank=False,help_text=u"域名ID")
    mailbox_id = models.IntegerField(u"MailBox", default=0)
    src_mailbox = models.CharField(u"远程帐号", max_length=200, null=True, blank=True)
    src_server = models.CharField(u"远程服务器", max_length=200, null=True, blank=True)
    src_password = models.CharField(u"密码", max_length=200, null=True, blank=True)
    disabled = models.CharField(u'激活状态', max_length=2, choices=constants.ACCOUNT_IMAPMOVING_DISABLE, null=False, blank=False, default="-1")

    class Meta:
        managed = False
        db_table = 'ext_popmail'

# ext_post_transfer
class PostTransfer(models.Model):

    mailbox_id = models.IntegerField(u"MailBox", default=0)
    mailbox = models.CharField(u"本地帐号", max_length=200, null=False, blank=True)

    server = models.CharField(u"远程服务器", max_length=200, null=True, blank=True)
    account = models.CharField(u"远程帐号", max_length=200, null=True, blank=True)
    recipient = models.CharField(u"收件帐号", max_length=200, null=True, blank=True)
    password = models.CharField(u"密码", max_length=200, null=True, blank=True)
    ssl = models.IntegerField(u'ssl登录', choices=constants.MAIL_TRANSFER_SSL, null=False, blank=False, default="-1")
    auth = models.IntegerField(u'需要验证', choices=constants.MAIL_TRANSFER_AUTH, null=False, blank=False, default="-1")
    fail_report = models.CharField(u"警告邮件地址", max_length=200, null=True, blank=True)
    disabled = models.CharField(u'激活状态', max_length=2, choices=constants.MAIL_TRANSFER_DISABLE, null=False, blank=False, default="-1")

    class Meta:
        managed = False
        db_table = 'ext_post_transfer'
