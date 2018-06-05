# -*- coding: utf-8 -*-
#
import time
import json
import base64
import smtplib

from lib.forms import BaseFied, DotDict, BaseCfilterActionFied, BaseCfilterOptionFied
from app.core.models import Domain, Mailbox, CoreAlias, DomainAttr, Department, CoreConfig
from app.setting.models import ExtCfilterRuleNew, ExtCfilterNewCond, ExtCfilterNewAction
from app.setting.models import AccountTransfer, IMAPMoving, POP3Moving, PostTransfer
from app.setting import constants
from lib import validators
from lib.formats import dict_compatibility
from lib.tools import clear_redis_cache
from lib.tools import create_task_trigger, add_task_to_queue
from django_redis import get_redis_connection

from django import forms
from django.utils.translation import ugettext_lazy as _

class SystemSetForm(DotDict):

    Fields = (
        # field, defaulte
        (u'greylist', '-1'), # 灰名单
        (u'recipientlimit', '100'), # 收件人数量限制
        (u'notice_lang', '1'), # 语言设置
        (u'login_domaincheck', '1'), # 登录域名检测
        (u'auto_backup', '-1'), # 数据备份
        (u'sys_search_mails', '-1'), # 数据
        (u'sys_auto_backup_mail','-1') # 自动转移到"旧邮件备份"目录
    )

    #旧版本webmail管理后台的设置，数据有点乱，这里新版也要兼容一下
    #尽量把以前放在不同页面的全局设置放到同一个页面下
    Fields_2 = (
        (u'sys_pass_all_local', '-1'), # 发信时对同域名无效用户进行退信
    )

    def __init__(self, post=None):
        self.post = post
        self.is_post = False
        self.__initialize()
        self.__valid = True

    def __initialize(self):
        data = {}
        if self.post:
            data = self.post
            self.is_post = True
        self.greylist_old = ""
        self.greylist_new = ""
        for k, v in self.Fields:
            if not self.is_post:
                vr = CoreConfig.analyseFormValue(function=k)
                v = vr if vr else v
            if k == u"greylist":
                vr = CoreConfig.analyseFormValue(function=k)
                self.greylist_old = vr if vr else v
                self.greylist_new = data.get(k, v)
            self[k] = BaseFied(value=data.get(k, v), error=None)
        for k, v in self.Fields_2:
            instance = DomainAttr.objects.filter(domain_id=0,type="system",item=k).first()
            if instance:
                v = instance.value
            self[k] = BaseFied(value=data.get(k, v), error=None)

    def is_valid(self):
        self.__check()
        return self.__valid

    def __check(self):
        obj = getattr(self, "recipientlimit")
        if obj and int(obj.value) < 0:
            self.__valid = False
            obj.set_error(_(u"收件人数量限制不能小于0."))

    def save(self):
        for k, v in self.Fields:
            obj = getattr(self, k)
            enabled, param = CoreConfig.analyseFormParam(k, obj.value)
            CoreConfig.saveFuction(function=k, enabled=enabled, param=param)
        for k, v in self.Fields_2:
            obj = getattr(self, k)
            DomainAttr.saveAttrObjValue(domain_id=0, type="system", item=k, value=obj.value)
        clear_redis_cache()
        if self.greylist_old != self.greylist_new:
            redis = get_redis_connection()
            redis.rpush("task_queue:apply_setting", "postfix")

class CoreAliasForm(DotDict):
    def __init__(self, instance=None, get=None, post=None):
        self.instance = instance
        self.get = get or {}
        self.post = post or {}
        self.__initialize()
        self.__valid = True
        self.domain_id = 0

    def __initialize(self):
        if self.post or (self.get and not self.instance):
            self.__setparam()
        elif self.instance:
            self.source = BaseFied(value=self.instance.source[1:], error=None)
            self.target = BaseFied(value=self.instance.target[1:], error=None)
            self.disabled = BaseFied(value=self.instance.disabled, error=None)
        else:
            self.__setparam()

    def __setparam(self):
        data = self.post if self.post else self.get
        self.source = BaseFied(value=data.get("source", ""), error=None)
        if self.instance:
            self.source = BaseFied(value=self.instance.source[1:], error=None)
        self.target = BaseFied(value=data.get("target", ""), error=None)
        disabled = data.get("disabled", "-1")
        if disabled not in ("-1", "1"):
            disabled = "-1"
        self.disabled = BaseFied(value=disabled, error=None)

    def is_valid(self):
        self.__check()
        return self.__valid

    def __check(self):

        if not self.instance and not validators.check_email_ordomain(u"@{}".format(self.source.value)):
            self.__valid = False
            self.source.set_error(u"虚拟邮件域不正确")
            return

        if not validators.check_email_ordomain(u"@{}".format(self.target.value)):
            self.__valid = False
            self.target.set_error(u"虚拟邮件域 不正确")
            return

        obj = Domain.objects.filter(domain=self.target.value).first()
        if not obj:
            self.__valid = False
            self.target.set_error(u"真实域名不存在，请重新选择")
            return
        else:
            self.domain_id = obj.id

        if not self.instance and Domain.objects.filter(domain=self.source.value).exists():
            self.__valid = False
            self.source.set_error(u"虚拟邮件域 不能填写真实域名")
            return

        # 校验唯一性
        if not self.instance and CoreAlias.objects.filter(
                source=u"@{}".format(self.source.value) ).exists():
            self.__valid = False
            self.source.set_error(u"虚拟邮件域 已在域别名列表中")
            return

        # 校验唯一性
        lists = CoreAlias.objects.filter( target=u"@{}".format(self.target.value) )
        if self.instance:
            lists = lists.exclude(id=self.instance.id)
        if lists.exists():
            self.__valid = False
            self.target.set_error(u"真实邮件域 已在域别名列表中")
            return

    def save(self):
        if self.instance:
            obj = self.instance
            obj.target = u"@{}".format(self.target.value)
            obj.domain_id = self.domain_id
            obj.disabled = self.disabled.value
            obj.save()
        else:
            CoreAlias.objects.create(
                domain_id=self.domain_id, type="domain",
                source=u"@{}".format(self.source.value),
                target=u"@{}".format(self.target.value),
                disabled=self.disabled.value
            )
        clear_redis_cache()

    def getDomainList(self):
        return Domain.objects.all()


class ExtCfilterRuleNewForm(object):

    ###########################################################
    # 动作列表
    ACTION_TYPE = constants.ALL_ACTION
    # 动作只有 action
    Action_only = ("break", "flag", "label", "delete", "sequester")


    # 动作有 action value
    # 动作有 action value 并下拉选择的
    Action_only_select = ("move_to", "copy_to")
    Action_only_slect_value = (
        ("Spam", u"垃圾箱"),
        ("Trash", u"废件箱"),
        ("Inbox", u"收件箱"),
        ("Sent", u"发件箱"),
    )
    # 动作有 action value  整型输入框
    Action_only_int = ("jump_to", )
    # 动作有 action value  字符串输入框
    Action_only_str = ("forward", "delete_header") # delete_header     value = { 'field':邮件头字段 }
    # 动作有 action value  编辑器
    Action_only_edit = ("append_body", )  #append_header     value = { 'field':邮件头字段, 'value':前端存入的值 }

    # 动作有 action field value
    Action_has_all = ("append_header", "replace_subject", "replace_body")

    # 动作复杂 mail
    Action_only_mail = ("mail", ) # value = { 'sender':发信人,'recipient':收信人,'subject':主题,'content':内容,'content_type':plain or html }
    Action_only_mail_type = (
        ("html", u"html内容"),
        ("plain", u"纯文本"),
    )

    Action_only_smtptransfer = ("smtptransfer",) #value = { 'account':登录帐号,'server':服务器,'ssl':是否SSL,'auth':是否验证,'password':base64_encode(password) }

    ###########################################################
    # 条件列表
    COND_LOGIC = constants.COND_LOGIC
    # 条件类型
    ALL_CONDITION_SUBOPTION = constants.ALL_CONDITION_SUBOPTION
    #### 条件动作
    # 1. 可以为 not_in , in 的  option  # 部门下拉选择  3个
    G_COND_OPTION_IN_T = constants.G_COND_OPTION_IN_T
    G_COND_ACTION_IN_T = constants.G_COND_ACTION_IN_T
    G_COND_OPTION_IN = constants.G_COND_OPTION_IN
    G_COND_ACTION_IN = constants.G_COND_ACTION_IN

    # 可以为 >= , <= 的 option  邮件大小  1个
    G_COND_OPTION_GTE_T = constants.G_COND_OPTION_GTE_T
    G_COND_ACTION_GTE_T = constants.G_COND_ACTION_GTE_T
    G_COND_OPTION_GTE = constants.G_COND_OPTION_GTE
    G_COND_ACTION_GTE = constants.G_COND_ACTION_GTE

    # 特殊设置的 option 只能为 ==  2个
    G_COND_OPTION_EQ_T = constants.G_COND_OPTION_EQ_T
    G_COND_ACTION_EQ_T = constants.G_COND_ACTION_EQ_T
    G_COND_OPTION_EQ = constants.G_COND_OPTION_EQ
    G_COND_ACTION_EQ = constants.G_COND_ACTION_EQ
    G_COND_ACTION_EQ_VALUE = constants.G_COND_ACTION_EQ_VALUE

    # 通用
    G_COND_OPTION_OTHER_T = constants.G_COND_OPTION_OTHER_T
    G_COND_ACTION_OTHER_T = constants.G_COND_ACTION_OTHER_T
    G_COND_OPTION_OTHER = constants.G_COND_OPTION_OTHER
    G_COND_ACTION_OTHER = constants.G_COND_ACTION_OTHER

    # 自定义
    G_COND_OPTION_ALL = constants.G_COND_OPTION_ALL

    def __init__(self, instance=None, post=None):
        self.__instance = instance
        self.__post = post
        self.__valid = True
        self.__initialize()

    def is_valid(self):
        self.__check()
        return self.__valid

    def save(self):
        # 主表
        if self.__instance:
            obj = self.__instance
            obj.name = self.name.value
            obj.type = self.type.value
            obj.logic = self.logic.value
            obj.sequence = self.sequence.value
            obj.disabled = self.disabled.value
            obj.save()
        else:
            obj = ExtCfilterRuleNew.objects.create(
                name=self.name.value, type=self.type.value,
                logic=self.logic.value, sequence=self.sequence.value, disabled=self.disabled.value
            )

        rule_id = obj.id
        # 先删除
        obj.deleteOptions()
        obj.deleteActions()

        # 动作
        bulk_action = []
        for d in self.cfilteraction.value:
            bulk_action.append( ExtCfilterNewAction( rule_id=rule_id, action=d.action, value=d.json_value, sequence=d.sequence ))
        ExtCfilterNewAction.objects.bulk_create(bulk_action)

        # 条件
        for d in self.cfilteroption.value:
            option_obj = ExtCfilterNewCond.objects.create(
                rule_id=rule_id, logic=d.logic, option=d.option,
                suboption=d.suboption, action=d.action, value=d.value
            )
            for dd in d.childs:
                ExtCfilterNewCond.objects.create(
                    rule_id=rule_id, parent_id=option_obj.id, logic=d.logic, option=dd.option,
                    suboption=dd.suboption, action=dd.action, value=dd.value
                )
        clear_redis_cache()
        #每次保存规则，都会自动开启新旧版本的内容过滤器开关
        obj = DomainAttr.getAttrObj(domain_id=0, type="system", item='sw_use_cfilter_new')
        obj.domain_id=0
        obj.type="system"
        obj.item="sw_use_cfilter_new"
        obj.value=1
        obj.save()

    def DepartMent(self):
        return Department.objects.all()

    def __check(self):
        pass

    def __initialize(self):
        if self.__post:
            post = self.__post
            name = post.get("name", "")
            error = None
            if not name:
                self.__valid = False
                error = u"规则名称不能为空"
            self.name = BaseFied(value=name, error=error)
            self.sequence = BaseFied(value=post.get("sequence", "999"), error=None)
            ltype = post.get("type", "-1").strip()
            ltype = int(ltype) if ltype in ("1", "-1") else 1
            self.type = BaseFied(value=ltype, error=None)
            disabled = post.get("disabled", "-1").strip()
            disabled = int(disabled) if disabled in ("1", "-1") else -1
            self.disabled = BaseFied(value=disabled, error=None)

            ###########################################################
            # 条件处理
            logic = self.__post.get("logic", "all").strip()
            logic = logic if logic in ("all", "one") else "all"
            self.logic = BaseFied(value=logic, error=None)

            options = []
            opt_error = False
            cfilteroptions = post.getlist('cfilteroptions[]', '')
            cfilteroptionchilds = post.getlist('cfilteroptionchilds[]', '')
            for this_id in cfilteroptions:

                this_id_bak = this_id.replace("--", "")
                action = ""
                value = ""
                childs = []
                error = None
                logic = post.get("option_logic_type{}".format(this_id), "all").strip()
                suboption = post.get("option_suboption{}".format(this_id), "").strip()
                if suboption in constants.ALL_CONDITION_OPTION_HEADER_VALUE:
                    option = "header"
                else:
                    option = "extra"

                if suboption in self.G_COND_OPTION_IN:
                    action = post.get("option_action_dpt{}".format(this_id), "").strip()
                    if action not in self.G_COND_ACTION_IN:
                        error = _(u"未知错误1！")
                        opt_error=True
                    try:
                        value = post.get("option_value_dpt{}".format(this_id), "").strip()
                    except:
                        value = 0

                if suboption in self.G_COND_OPTION_GTE:
                    action = post.get("option_action_size{}".format(this_id), "").strip()
                    if action not in self.G_COND_ACTION_GTE:
                        error = _(u"未知错误2！")
                        opt_error=True
                    try:
                        value = int(post.get("option_value_size{}".format(this_id), "").strip())
                    except:
                        value = 0
                    if value <= 0:
                        error = _(u"邮件大小必须大于0！")
                        opt_error=True

                if suboption in self.G_COND_OPTION_EQ:
                    action = post.get("option_action_disabled{}".format(this_id), "").strip()
                    if action not in self.G_COND_ACTION_EQ:
                        error = _(u"未知错误3！")
                        opt_error=True

                    value = post.get("option_value_disabled{}".format(this_id), "-1").strip()
                    if value not in ("-1", "1"):
                        error = _(u"未知错误4！")
                        opt_error=True

                if suboption in self.G_COND_OPTION_OTHER:
                    action = post.get("option_action_other{}".format(this_id), "").strip()
                    if action not in self.G_COND_ACTION_OTHER:
                        error = _(u"未知错误5！")
                        opt_error=True
                    value = post.get("option_value_other{}".format(this_id), "").strip()
                    if not value:
                        error = _(u"不能为空！")
                        opt_error=True

                if not suboption:
                    error = _(u"未知错误6！")
                    opt_error=True

                format_c = "--{}".format(this_id_bak)
                this_childs = [ i for i in cfilteroptionchilds if i.endswith(format_c)]
                for this_child_id in this_childs:
                    sub_id = this_child_id.replace(format_c, "")
                    sub_action = ""
                    sub_value = ""
                    sub_error = None

                    sub_suboption = post.get("option_suboption{}".format(this_child_id), "").strip()
                    if sub_suboption in constants.ALL_CONDITION_OPTION_HEADER_VALUE:
                        sub_option = "header"
                    else:
                        sub_option = "extra"

                    if sub_suboption in self.G_COND_OPTION_IN:
                        sub_action = post.get("option_action_dpt{}".format(this_child_id), "").strip()
                        if sub_action not in self.G_COND_ACTION_IN:
                            sub_error = _(u"未知错误7！")
                            opt_error=True
                        try:
                            sub_value = post.get("option_value_dpt{}".format(this_child_id), "").strip()
                        except:
                            sub_value = 0

                    if sub_suboption in self.G_COND_OPTION_GTE:
                        sub_action = post.get("option_action_size{}".format(this_child_id), "").strip()
                        if sub_action not in self.G_COND_ACTION_GTE:
                            sub_error = _(u"未知错误8！")
                            opt_error=True
                        try:
                            sub_value = int(post.get("option_value_size{}".format(this_child_id), "").strip())
                        except:
                            sub_value = 0

                        if sub_value <= 0:
                            sub_error = _(u"邮件大小必须大于0！")
                            opt_error=True

                    if sub_suboption in self.G_COND_OPTION_EQ:
                        sub_action = post.get("option_action_disabled{}".format(this_child_id), "").strip()
                        if sub_action not in self.G_COND_ACTION_EQ:
                            sub_error = _(u"未知错误9！")
                            opt_error=True

                        sub_value = post.get("option_value_disabled{}".format(this_child_id), "-1").strip()
                        if sub_value not in ("-1", "1"):
                            sub_error = _(u"未知错误10！")
                            opt_error=True

                    if sub_suboption in self.G_COND_OPTION_OTHER:
                        sub_action = post.get("option_action_other{}".format(this_child_id), "").strip()
                        if sub_action not in self.G_COND_ACTION_OTHER:
                            sub_error = _(u"未知错误11！： %s"%sub_action)
                            opt_error=True
                        sub_value = post.get("option_value_other{}".format(this_child_id), "").strip()
                        if not sub_value:
                            sub_error = _(u"输入不能为空！")
                            opt_error=True

                    if not sub_suboption:
                        sub_error = _(u"未知错误12！")
                        opt_error=True

                    T1 = BaseCfilterOptionFied(
                        id=sub_id, parent_id=this_id_bak, logic=logic, option=sub_option, suboption=sub_suboption,
                        action=sub_action, value=sub_value, error=sub_error
                    )
                    childs.append(T1)

                T = BaseCfilterOptionFied(
                    id=this_id_bak, parent_id="", logic=logic, option=option, suboption=suboption,
                    action=action, value=value, error=error, childs=childs
                )
                options.append(T)

            if opt_error:
                self.__valid = False
            self.cfilteroption = BaseFied(value=options, error=opt_error)

            ###########################################################
            # 动作处理
            acts=[]
            index = 1
            opt_error = False
            cfilteractionids = post.getlist('cfilteractionids[]', '')
            for rid in cfilteractionids:
                error = None
                field = ""
                value = ""
                mail_sender=""
                mail_recipient=""
                mail_subject=""
                mail_type="html"
                mail_content_html=""
                mail_content_plain=""
                trans_server = ""
                trans_account = ""
                trans_password = ""
                trans_ssl = ""
                trans_auth = ""

                sequence = post.get('action_sequence{}'.format(rid), "")
                json_value = json.dumps({"value": None})
                action_type = post.get('action_type{}'.format(rid), "")

                if action_type in self.Action_only_int:
                    value = post.get("action_value_int{}".format(rid), "0")
                    json_value = json.dumps({"value": value})

                if action_type in self.Action_only_select:
                    value = post.get("action_value_select{}".format(rid), "")
                    json_value = json.dumps({"value": value})

                # Action_only_str
                if action_type in self.Action_only_str:
                    value = post.get("action_value_b{}".format(rid), "").strip()
                    if not value:
                        error = _(u"不能为空！")
                        opt_error=True
                    json_value = json.dumps({"value": value})
                    if action_type == "delete_header":
                        json_value = json.dumps({"field": value})

                # 动作有 action value  编辑器
                if action_type in self.Action_only_edit:
                    value = post.get("action_value_edit{}".format(rid), "").strip()
                    if not value:
                        error = _(u"请在编辑器输入追加内容！")
                        opt_error=True
                    json_value = json.dumps({"value": value})

                if action_type in self.Action_has_all:
                    field = post.get("action_field{}".format(rid), "").strip()
                    value = post.get("action_value_a{}".format(rid), "").strip()
                    if not field:
                        error = _(u"邮件头设置不能为空！")
                        opt_error=True
                    if field and not value:
                        error = _(u"邮件头设置值不能为空！")
                        opt_error=True
                    json_value = json.dumps({"field": field, "value": value})

                # 动作复杂 mail
                if action_type in self.Action_only_mail:
                    mail_sender = post.get("action_value_mail_sender{}".format(rid), "").strip()
                    mail_recipient = post.get("action_value_mail_recipient{}".format(rid), "").strip()
                    mail_subject = post.get("action_value_mail_subject{}".format(rid), "").strip()
                    mail_type = post.get("action_value_mail_type{}".format(rid), "").strip()
                    mail_content_html = post.get("action_value_mail_content_html{}".format(rid), "").strip()
                    mail_content_plain = post.get("action_value_mail_content_plain{}".format(rid), "").strip()
                    content = ""
                    if not mail_sender:
                        error = _(u"发信人不能为空！")
                        opt_error=True
                    if not mail_recipient:
                        error = _(u"收信人不能为空！")
                        opt_error=True
                    if not mail_subject:
                        error = _(u"主题不能为空！")
                        opt_error=True
                    if mail_type == "html":
                        content = mail_content_html
                    elif mail_type == "plain":
                        content = mail_content_plain
                    if not content:
                        error = _(u"邮件内容不能为空！")
                        opt_error=True
                    json_value = json.dumps({'sender':mail_sender, 'recipient':mail_recipient,'subject':mail_subject,'content':content,'content_type': mail_type})

                if action_type in self.Action_only_smtptransfer:
                    trans_server = post.get("action_value_smtptransfer_server{}".format(rid), "").strip()
                    trans_account = post.get("action_value_smtptransfer_account{}".format(rid), "").strip()
                    trans_password = post.get("action_value_smtptransfer_password{}".format(rid), "").strip()
                    trans_ssl = post.get("action_value_smtptransfer_ssl{}".format(rid), "").strip()
                    trans_auth = post.get("action_value_smtptransfer_auth{}".format(rid), "").strip()

                    if not trans_server:
                        error = _(u"服务器不能为空！")
                        opt_error=True
                    if not trans_account:
                        error = _(u"帐号不能为空！")
                        opt_error=True
                    if (trans_ssl=='1' or trans_auth=='1') and (not trans_password):
                        error = _(u"开启了ssl或需要验证密码后，密码不能为空！")
                        opt_error=True

                    if not trans_ssl:
                        trans_ssl = "-1"
                    if not trans_auth:
                        trans_auth = "-1"
                    trans_password = base64.encodestring(trans_password)
                    trans_password = trans_password.strip()
                    json_value = json.dumps({
                        'server':trans_server, 'account':trans_account,'password':trans_password,
                        'ssl':trans_ssl, 'auth': trans_auth
                        })
                    #end if

                acts.append( BaseCfilterActionFied(
                    id=index, action=action_type, field=field, value=value, error=error, sequence=sequence,
                    mail_sender=mail_sender, mail_recipient=mail_recipient, mail_subject=mail_subject, mail_type=mail_type,
                    mail_content_html=mail_content_html, mail_content_plain=mail_content_plain,
                    trans_server=trans_server, trans_account=trans_account, trans_password=trans_password,trans_ssl=trans_ssl, trans_auth=trans_auth,
                    json_value=json_value
                ) )
                index += 1

            if opt_error:
                self.__valid = False
            self.cfilteraction = BaseFied(value=acts, error=opt_error)

        elif self.__instance:
            obj = self.__instance
            self.name =  BaseFied(value=obj.name, error=None)
            self.sequence =  BaseFied(value=obj.sequence, error=None)
            self.type =  BaseFied(value=obj.type, error=None)
            self.disabled = BaseFied(value=obj.disabled, error=None)
            self.logic = BaseFied(value=obj.logic, error=None)

            actions = []
            for d in obj.getActions():

                field = ""
                value = ""
                mail_sender=""
                mail_recipient=""
                mail_subject=""
                mail_type="html"
                mail_content_html=""
                mail_content_plain=""

                trans_server = ""
                trans_account = ""
                trans_password = ""
                trans_ssl = ""
                trans_auth = ""

                action = d.action
                try:
                    j = json.loads(d.value)
                except:
                    j = {}
                if action == "delete_header":
                    field = dict_compatibility(j, "field")
                elif action in ("append_header","replace_subject","replace_body"):
                    field = dict_compatibility(j, "field")
                    value = dict_compatibility(j, "value")
                elif action == "mail":
                    mail_sender = dict_compatibility(j, "sender")
                    mail_recipient = dict_compatibility(j, "recipient")
                    mail_subject = dict_compatibility(j, "subject")
                    mail_type = dict_compatibility(j, "content_type")
                    if mail_type == "html":
                        mail_content_html = dict_compatibility(j, "content")
                    else:
                        mail_content_plain = dict_compatibility(j, "content")
                elif action == "smtptransfer":
                    trans_server = dict_compatibility(j, "server")
                    trans_account = dict_compatibility(j, "account")
                    trans_password = dict_compatibility(j, "password")
                    trans_ssl = dict_compatibility(j, "ssl")
                    trans_auth = dict_compatibility(j, "auth")

                    trans_password = base64.decodestring(trans_password)
                else:
                    value = dict_compatibility(j, "value")
                    if action in self.Action_only_int:
                        try:
                            value = int(value)
                        except:
                            value = 0

                T = BaseCfilterActionFied(
                    id=d.id, action=d.action, field=field, value=value, error=None, sequence=d.sequence,
                    mail_sender=mail_sender, mail_recipient=mail_recipient, mail_subject=mail_subject, mail_type=mail_type,
                    mail_content_html=mail_content_html, mail_content_plain=mail_content_plain,
                    trans_server=trans_server, trans_account=trans_account, trans_password=trans_password, trans_ssl=trans_ssl, trans_auth=trans_auth,
                    json_value=j
                )
                actions.append(T)
            self.cfilteraction = BaseFied(value=actions, error=None)

            options=[]
            for d in obj.getOptions():
                childs = []
                this_id = d.id
                logic = d.logic
                option = d.option
                suboption = d.suboption
                action = d.action
                value = d.value

                for dd in obj.getOptions(parent_id=this_id):
                    sub_id = dd.id
                    sub_parent_id = this_id
                    sub_logic = logic
                    sub_option = dd.option
                    sub_suboption = dd.suboption
                    sub_action = dd.action
                    sub_value = dd.value
                    T1 = BaseCfilterOptionFied(
                        id=sub_id, parent_id=sub_parent_id, logic=sub_logic, option=sub_option, suboption=sub_suboption,
                        action=sub_action, value=sub_value, error=None
                    )
                    childs.append(T1)

                T = BaseCfilterOptionFied(
                    id=this_id, parent_id="", logic=logic, option=option, suboption=suboption,
                    action=action, value=value, error=None, childs=childs
                )
                options.append(T)
            self.cfilteroption = BaseFied(value=options, error=None)
        else:
            self.name = BaseFied(value="", error=None)
            self.sequence = BaseFied(value="999", error=None)
            self.type = BaseFied(value=1, error=None)
            self.disabled = BaseFied(value=-1, error=None)
            self.logic = BaseFied(value="all", error=None)
            self.cfilteraction = BaseFied(value=[ BaseCfilterActionFied(id=0, action="break"),], error=None)
            self.cfilteroption = BaseFied(
                value=[
                    BaseCfilterOptionFied(
                        id=0, logic="all", option="extra", suboption="all_mail",
                        childs=[ BaseCfilterOptionFied(id=1, parent_id=0, logic="all", option="extra", suboption="all_mail", error=None) ] ) ],
                error=None)


#这个类目前没用了，改在webmail系统后台设置开关。 2018-01-19 lpx
class ExtCfilterConfigForm(object):

    def __init__(self, instance=None, get=None, post=None):
        self.instance = instance
        self.get = get or {}
        self.post = post or {}
        self.__initialize()
        self.__valid = True
        self.domain_id = 0

    def __initialize(self):
        if self.post or (self.get and not self.instance):
            self.__setparam()
        elif self.instance:
            self.value = BaseFied(value=self.instance.value, error=None)
        else:
            self.__setparam()

    def __setparam(self):
        data = self.post if self.post else self.get
        self.value = BaseFied(value=data.get("sw_new_cfilter_value", "0"), error=None)
        if self.instance:
            self.value = BaseFied(value=self.instance.value, error=None)

    def is_valid(self):
        self.__check()
        return self.__valid

    def __check(self):
        obj = getattr(self, "value")
        if not obj or int(obj.value) < 0:
            self.__valid = False
            obj.set_error(_(u"需要输入值"))
        return self.__valid

    def save(self):
        if self.instance:
            obj = self.instance
        else:
            obj = DomainAttr.getAttrObj(
                item="sw_use_cfilter_new", type="system", domain_id=0
            )
        obj.domain_id=self.domain_id
        obj.type="system"
        obj.item="sw_use_cfilter_new"
        obj.value=self.value.value
        obj.save()
        clear_redis_cache()


class SmtpSetForm(forms.Form):

    smtp_seta = forms.IntegerField(label=u"第1次重试", required=True,min_value=1, help_text=u"与上次发送间隔，单位：分钟。")
    smtp_setb = forms.IntegerField(label=u"第2次重试", required=True, min_value=1, help_text=u"与上次发送间隔，单位：分钟。") # max_value=120
    smtp_setc = forms.IntegerField(label=u"第3次重试", required=True, min_value=1, help_text=u"与上次发送间隔，单位：分钟。")

    def save(self):
        smtp_seta = self.cleaned_data['smtp_seta']
        smtp_setb = self.cleaned_data['smtp_setb']
        smtp_setc = self.cleaned_data['smtp_setc']
        DomainAttr.saveAttrObjValue(item="cf_smtp_retry", value=json.dumps({
            "1th": smtp_seta, "2nd": smtp_setb, "3rd": smtp_setc
        }))
        clear_redis_cache()


class AccountTransferForm(DotDict):

    PARAM_LIST = dict((
        (u'succ_del', u'-1'),
        (u'status', u'wait'),
        (u'last_update', u'0000-00-00 00:00:00'),
        (u'desc_msg', u''),
        (u'disabled', u'-1'),
    ))


    def __init__(self, instance=None, get=None, post=None):
        self.instance = instance
        self.get = get or {}
        self.post = post or {}
        self.__initialize()
        self.__valid = True

    def __initialize(self):
        self.maildata = BaseFied(value="0", error=None)
        self.netdisk = BaseFied(value="0", error=None)
        self.contact = BaseFied(value="0", error=None)
        self.mailbox_id = BaseFied(value=0, error=None)
        self.mailbox = BaseFied(value="", error=None)
        self.mailbox_to = BaseFied(value="", error=None)
        self.mailbox_disabled = False

        if self.instance:
            self.mailbox_id = BaseFied(value=self.instance.mailbox_id, error=None)
            self.mailbox = BaseFied(value=self.instance.mailbox, error=None)
            self.mailbox_to = BaseFied(value=self.instance.mailbox_to, error=None)

        if self.post or (self.get and not self.instance):
            self.__setparam()
        elif self.instance:
            mode = self.instance.mode
            if mode:
                mode = json.loads(mode)
            mode = {} if not mode else mode
            if "maildata" in mode:
                self.maildata = BaseFied(value=str(mode["maildata"]), error=None)
            if "netdisk" in mode:
                self.netdisk = BaseFied(value=str(mode["netdisk"]), error=None)
            if "contact" in mode:
                self.contact = BaseFied(value=str(mode["contact"]), error=None)

            self.succ_del = BaseFied(value=self.instance.succ_del, error=None)
            self.status = BaseFied(value=self.instance.status, error=None)
            self.last_update = BaseFied(value=self.instance.last_update, error=None)
            self.desc_msg = BaseFied(value=self.instance.desc_msg, error=None)
            self.disabled = BaseFied(value=self.instance.disabled, error=None)
        else:
            self.__setparam()

        obj = Mailbox.objects.filter(mailbox=self.mailbox.value).first()
        if not obj or int(obj.disabled) != 1:
            self.mailbox_disabled = False
        else:
            self.mailbox_disabled = True

    def __setparam(self):
        data = self.post if self.post else self.get
        for key,default in self.PARAM_LIST.items():
            if data:
                obj = BaseFied(value=data.get(key, default), error=None)
            elif self.instance:
                obj = BaseFied(value=getattr(self.instance, key), error=None)
            else:
                obj = BaseFied(value=default, error=None)
            setattr(self,key,obj)

        if data:
            if "maildata" in data:
                self.maildata = BaseFied(value=str(data["maildata"]), error=None)
            if "netdisk" in data:
                self.netdisk = BaseFied(value=str(data["netdisk"]), error=None)
            if "contact" in data:
                self.contact = BaseFied(value=str(data["contact"]), error=None)
        if data.get("mailbox",""):
            self.mailbox = BaseFied(value=data["mailbox"], error=None)
            obj = Mailbox.objects.filter(mailbox=data["mailbox"]).first()
            mailbox_id = obj.id if obj else 0
            self.mailbox_id = BaseFied(value=mailbox_id, error=None)
        if data.get("mailbox_to",""):
            self.mailbox_to = BaseFied(value=data["mailbox_to"], error=None)

    def is_valid(self):
        self.__check()
        return self.__valid

    def __check(self):
        if not self.instance:
            if not validators.check_email_ordomain(u"{}".format(self.mailbox.value)):
                self.__valid = False
                self.mailbox.set_error(u"邮箱格式不正确")
            if not validators.check_email_ordomain(u"{}".format(self.mailbox_to.value)):
                self.__valid = False
                self.mailbox_to.set_error(u"邮箱格式不正确")
        if self.maildata.value != "1" and self.netdisk.value != "1" and self.contact.value != "1":
            self.__valid = False
            self.maildata.set_error(u"至少需要选择一种迁移模式")

        if self.instance:
            if self.instance.status in ("deleting","deleted","finished"):
                self.__valid = False
                self.mailbox.set_error(u"'删除'和'结束'阶段的数据，只能删除不能修改")

        if not self.mailbox_disabled:
            self.__valid = False
            self.mailbox.set_error(u"迁移的帐号尚未禁用，无法删除")

        if int(self.mailbox_id.value) <= 0 :
            self.__valid = False
            self.mailbox.set_error(u"无效的邮箱帐号")

        obj = Mailbox.objects.filter(mailbox=self.mailbox_to.value).first()
        if not obj or int(obj.disabled) != -1:
            self.__valid = False
            self.mailbox_to.set_error(u"目标帐号必须是一个非禁用状态下的有效帐号")

        if not self.instance:
            obj2 = AccountTransfer.objects.filter(mailbox=self.mailbox.value,mailbox_to=self.mailbox_to.value).first()
            if obj2:
                self.__valid = False
                self.mailbox_to.set_error(u"迁移列表中已存在相同的迁移数据")

        return self.__valid

    def save(self):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        mode = {
            "maildata"  :   self.maildata.value,
            "netdisk"   :   self.netdisk.value,
            "contact"   :   self.contact.value,
        }
        mode = json.dumps( mode )

        if self.instance:
            obj = self.instance
            obj.mode = u"{}".format(mode)
            obj.succ_del = u"{}".format(self.succ_del.value)
            obj.last_update = u"{}".format(now)
            obj.disabled = self.disabled.value
            obj.save()
        else:
            AccountTransfer.objects.create(
                mailbox_id=self.mailbox_id.value,
                mailbox=u"{}".format(self.mailbox.value),
                mailbox_to=u"{}".format(self.mailbox_to.value),
                mode=u"{}".format(mode),
                succ_del=u"{}".format(self.succ_del.value),
                status=u"{}".format(self.status.value),
                desc_msg=u"{}".format(self.desc_msg.value),
                last_update=u"{}".format(now),
                disabled=self.disabled.value
            )
        clear_redis_cache()

    @property
    def mailboxLists(self):
        return Mailbox.objects.all()


class IMAPMovingForm(DotDict):

    PARAM_LIST = dict((
        (u'mailbox', u''),
        (u'src_mailbox',u''),
        (u'src_server',u''),
        (u'ssl',u'-1'),
        (u'src_password',u''),
        (u'src_folder',u'all'),
        (u'status', u'wait'),
        (u'last_update', u'0000-00-00 00:00:00'),
        (u'desc_msg', u''),
        (u'disabled', -1),
    ))


    def __init__(self, instance=None, get=None, post=None):
        self.instance = instance
        self.get = get or {}
        self.post = post or {}
        self.__initialize()
        self.__valid = True

    def __initialize(self):
        self.mailbox_id = BaseFied(value=0, error=None)
        self.mailbox = BaseFied(value="", error=None)
        self.src_mailbox = BaseFied(value="", error=None)
        self.src_server = BaseFied(value="", error=None)
        self.ssl = BaseFied(value="-1", error=None)
        self.src_password = BaseFied(value="", error=None)
        self.src_folder = BaseFied(value="all", error=None)
        self.status = BaseFied(value="wait", error=None)
        self.last_update = BaseFied(value="", error=None)
        self.desc_msg = BaseFied(value="", error=None)

        if self.instance:
            self.mailbox = BaseFied(value=self.instance.mailbox, error=None)

        if self.post or (self.get and not self.instance):
            self.__setparam()
        elif self.instance:
            self.mailbox = BaseFied(value=self.instance.mailbox, error=None)
            self.src_mailbox = BaseFied(value=self.instance.src_mailbox, error=None)
            self.src_server = BaseFied(value=self.instance.src_server, error=None)
            self.ssl = BaseFied(value=self.instance.ssl, error=None)
            self.src_password = BaseFied(value=self.instance.src_password, error=None)
            self.src_folder = BaseFied(value=self.instance.src_folder, error=None)
            self.status = BaseFied(value=self.instance.status, error=None)
            self.last_update = BaseFied(value=self.instance.last_update, error=None)
            self.desc_msg = BaseFied(value=self.instance.desc_msg, error=None)
            self.disabled = BaseFied(value=self.instance.disabled, error=None)
        else:
            self.__setparam()

    def __setparam(self):
        data = self.post if self.post else self.get
        for key,default in self.PARAM_LIST.items():
            if data:
                obj = BaseFied(value=data.get(key, default), error=None)
            elif self.instance:
                obj = BaseFied(value=getattr(self.instance, key), error=None)
            else:
                obj = BaseFied(value=default, error=None)
            setattr(self,key,obj)

        if data.get("mailbox",""):
            self.mailbox = BaseFied(value=data["mailbox"], error=None)
            obj = Mailbox.objects.filter(mailbox=data["mailbox"]).first()
            mailbox_id = obj.id if obj else 0
            self.mailbox_id = BaseFied(value=mailbox_id, error=None)

    def is_valid(self):
        self.__check()
        return self.__valid

    def __check(self):
        if not self.instance:
            if not validators.check_email_ordomain(u"{}".format(self.mailbox.value)):
                self.__valid = False
                self.mailbox.set_error(u"邮箱格式不正确")

        if int(self.mailbox_id.value) <= 0 :
            self.__valid = False
            self.mailbox.set_error(u"无效的本地邮箱帐号")

        obj2 = POP3Moving.objects.filter(mailbox_id=self.mailbox_id.value,src_mailbox=self.src_mailbox.value).first()
        if obj2:
            self.__valid = False
            self.mailbox.set_error(u"该用户已经在“邮箱搬家”设置了相同的迁移任务")
        return self.__valid

    def save(self):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        set_from = "admin"
        if self.instance:
            obj = self.instance
            obj.mailbox_id=u"{}".format(self.mailbox_id.value)
            obj.mailbox=u"{}".format(self.mailbox.value)
            obj.src_mailbox=u"{}".format(self.src_mailbox.value)
            obj.src_server=u"{}".format(self.src_server.value)
            obj.ssl=u"{}".format(self.ssl.value)
            obj.src_password=u"{}".format(self.src_password.value)
            obj.src_folder=u"{}".format(self.src_folder.value)
            obj.set_from=u"{}".format(set_from)
            obj.status=u"{}".format(self.status.value)
            obj.desc_msg=u"{}".format(self.desc_msg.value)
            obj.last_update=u"{}".format(now)
            obj.disabled=self.disabled.value
            obj.save()
        else:
            IMAPMoving.objects.create(
                mailbox_id=u"{}".format(self.mailbox_id.value),
                mailbox=u"{}".format(self.mailbox.value),
                src_mailbox=u"{}".format(self.src_mailbox.value),
                src_server=u"{}".format(self.src_server.value),
                ssl=u"{}".format(self.ssl.value),
                src_password=u"{}".format(self.src_password.value),
                src_folder=u"{}".format(self.src_folder.value),
                set_from=u"{}".format(set_from),
                status=u"{}".format(self.status.value),
                desc_msg=u"{}".format(self.desc_msg.value),
                last_update=u"{}".format(now),
                disabled=self.disabled.value
            )
        data = {
            "mailbox_id"   :   self.mailbox_id.value,
            "src_mailbox"  :  self.src_mailbox.value,
        }
        add_task_to_queue("imapmail",data)

    @property
    def mailboxLists(self):
        return Mailbox.objects.all()

class IMAPMovingImportForm(DotDict):

    COL_LIST = [
        "mailbox",  "src_mailbox",  "src_server",   "src_password",     "ssl",
    ]

    def __init__(self, get=None, post=None):
        self.get = get or {}
        self.post = post or {}
        self.__valid = True
        self.data_list = []
        self.insert_list = []
        self.fail_list = []
        self.__initialize()

    def __initialize(self):
        data = self.post if self.post else self.get
        import_data = ""
        if "import_data" in data:
            import_data = data["import_data"]

        import_data = import_data.replace("\r\n","\n")
        import_data = import_data.replace("\r","\n")

        for line in import_data.split("\n"):
            line = self.join_string(line)
            if not line:
                continue
            data = {}
            for idx,col in enumerate(line.split("\t")):
                if idx >= len(self.COL_LIST):
                    break
                col_name = self.COL_LIST[idx]
                if col.upper() in ("${EMPTY}","EMPTY"):
                    col = ""
                data[ col_name ] = col
                if col_name == "mailbox":
                    obj = Mailbox.objects.filter(mailbox=col).first()
                    mailbox_id = 0 if not obj else obj.id
                    data[ "mailbox_id" ] = mailbox_id
            if not data:
                continue
            self.data_list.append( (line,data) )

    def join_string(self, line):
        code_1 = []
        code_2 = []
        for s in line:
            s = s.strip()
            if not s:
                if code_1:
                    code_2.append( "".join(code_1) )
                    code_1 = []
                continue
            code_1.append( s )
        if code_1:
            code_2.append( "".join(code_1) )
        return "\t".join(code_2)

    def is_valid(self):
        self.__check()
        return self.__valid

    def __check(self):
        self.insert_list = []
        for line,data in self.data_list:
            mailbox = data.get("mailbox","").strip()
            src_mailbox = data.get("src_mailbox","").strip()
            src_server = data.get("src_server","").strip()
            ssl = data.get("ssl","0")
            src_password = data.get("src_password","0")
            mailbox_id = data.get("mailbox_id","0")

            if not mailbox or not src_mailbox or not src_server:
                code = u"本地帐号、远程帐号、远程服务器信息不全： %s"%line
                self.fail_list.append( code )
                continue
            if not validators.check_email_ordomain(u"{}".format(mailbox)):
                code = u"本地帐号 '%s' 格式不正确, 插入数据： %s"%(mailbox,line)
                self.fail_list.append( code )
                continue
            if not validators.check_email_ordomain(u"{}".format(src_mailbox)):
                code = u"远程帐号 '%s' 格式不正确, 插入数据： %s"%(src_mailbox,line)
                self.fail_list.append( code )
                continue
            obj = Mailbox.objects.filter(mailbox=mailbox).first()
            if not obj:
                code = u"本地帐号 '%s' 不存在, 插入数据： %s"%(mailbox,line)
                self.fail_list.append( code )
                continue
            obj2 = POP3Moving.objects.filter(mailbox_id=mailbox_id,src_mailbox=src_mailbox).first()
            if obj2:
                code = u"本地帐号 '%s' 已经在“邮箱搬家”设置了相同的迁移任务, 插入数据： %s"%(mailbox,line)
                self.fail_list.append( code )
                continue
            data[ "mailbox_id" ] = obj.id
            self.insert_list.append( data )
        return self.__valid

    def save(self):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        set_from = u"file"

        for data in self.insert_list:
            mailbox = data.get("mailbox","")
            src_mailbox = data.get("src_mailbox","")
            src_server = data.get("src_server","")
            ssl = data.get("ssl","0")
            src_password = data.get("src_password","0")
            mailbox_id = data.get("mailbox_id","0")

            try:
                obj = IMAPMoving.objects.filter(mailbox=mailbox,src_mailbox=src_mailbox).first()
                if obj:
                    obj.mailbox_id=u"{}".format(mailbox_id)
                    obj.mailbox=u"{}".format(mailbox)
                    obj.src_mailbox=u"{}".format(src_mailbox)
                    obj.src_server=u"{}".format(src_server)
                    obj.ssl=u"{}".format(ssl)
                    obj.src_password=u"{}".format(src_password)
                    obj.set_from=set_from
                    obj.last_update=u"{}".format(now)
                    obj.save()
                else:
                    status = "wait"
                    IMAPMoving.objects.create(
                        mailbox_id=u"{}".format(mailbox_id),
                        mailbox=u"{}".format(mailbox),
                        src_mailbox=u"{}".format(src_mailbox),
                        src_server=u"{}".format(src_server),
                        ssl=u"{}".format(ssl),
                        src_password=u"{}".format(src_password),
                        set_from=u"{}".format(set_from),
                        status=u"{}".format(status),
                        last_update=u"{}".format(now),
                    )
            except Exception,err:
                code = u"数据格式不符合要求： %s"%data
                self.fail_list.append( code )
        add_task_to_queue("imapmail",{})


class MailTransferSenderForm(DotDict):

    PARAM_LIST = dict((
        (u'account',u''),
        (u'server',u''),
        (u'password',u''),
        (u'ssl',u'-1'),
        (u'auth',u'1'),
        (u'disabled',u'-1'),
    ))

    def __init__(self, instance=None, get=None, post=None):
        self.instance = instance
        self.get = get or {}
        self.post = post or {}
        self.__initialize()
        self.__valid = True

    def __initialize(self):
        self.account = BaseFied(value="", error=None)
        self.server = BaseFied(value="", error=None)
        self.password = BaseFied(value="", error=None)
        self.ssl = BaseFied(value="-1", error=None)
        self.auth = BaseFied(value="1", error=None)
        self.disabled = BaseFied(value="-1", error=None)

        if self.post or (self.get and not self.instance):
            self.__setparam()
        else:
            value = self.__get_instance_value()
            if value:
                account = value["account"]
                server = value["server"]
                ssl = value["ssl"]
                auth = value["auth"]
                password = value["password"]
                disabled = value["disabled"]
                self.account = BaseFied(value=account, error=None)
                self.server = BaseFied(value=server, error=None)
                self.ssl = BaseFied(value=ssl, error=None)
                self.auth = BaseFied(value=auth, error=None)
                self.disabled = BaseFied(value=disabled, error=None)

                password = base64.decodestring(password)
                self.password = BaseFied(value=password, error=None)
            else:
                self.__setparam()

    def __get_instance_value(self):
        if not self.instance:
            return {}
        try:
            value = json.loads(self.instance.value)
            for k,default in self.PARAM_LIST.items():
                if not k in value:
                    value[k] = default
            return value
        except:
            return {}

    def __setparam(self):
        data = self.post if self.post else self.get
        for key,default in self.PARAM_LIST.items():
            if data:
                obj = BaseFied(value=data.get(key, default), error=None)
            else:
                obj = BaseFied(value=default, error=None)
            setattr(self,key,obj)

    def is_valid(self):
        self.__check()
        return self.__valid

    def __check(self):
        return True

    def save(self):
        if self.instance:
            obj = self.instance
        else:
            obj = DomainAttr.getAttrObj(
                item="deliver_transfer_sender", type="system", domain_id=0
            )
        password = base64.encodestring(self.password.value)
        value = {
            "account"   :   self.account.value,
            "server"    :   self.server.value,
            "password"  :   password,
            "ssl"       :   self.ssl.value,
            "auth"       :   self.auth.value,
            "disabled"  :   self.disabled.value,
        }
        value = json.dumps( value )
        obj.domain_id=0
        obj.type="system"
        obj.item="deliver_transfer_sender"
        obj.value=value
        obj.save()

class PostTransferForm(DotDict):

    PARAM_LIST = dict((
        (u'mailbox_id', u''),
        (u'account',u''),
        (u'recipient',u''),
        (u'server',u''),
        (u'password',u''),
        (u'ssl',u'-1'),
        (u'auth',u'1'),
        (u'disabled', u'-1'),
        (u'fail_report', u''),
    ))


    def __init__(self, instance=None, get=None, post=None):
        self.instance = instance
        self.get = get or {}
        self.post = post or {}
        self.__initialize()
        self.__valid = True

    def __initialize(self):
        self.mailbox_id = BaseFied(value=0, error=None)
        self.mailbox = BaseFied(value="", error=None)

        self.account = BaseFied(value="", error=None)
        self.recipient = BaseFied(value="", error=None)
        self.server = BaseFied(value="", error=None)
        self.password = BaseFied(value="", error=None)
        self.ssl = BaseFied(value="-1", error=None)
        self.auth = BaseFied(value="1", error=None)
        self.fail_report = BaseFied(value="", error=None)

        if self.post or (self.get and not self.instance):
            self.__setparam()
        elif self.instance:
            self.mailbox_id = BaseFied(value=self.instance.mailbox_id, error=None)
            obj = Mailbox.objects.filter(id=self.instance.mailbox_id).first()
            mailbox = obj.mailbox if obj else ""
            self.mailbox = BaseFied(value=mailbox, error=None)

            self.account = BaseFied(value=self.instance.account, error=None)
            self.recipient = BaseFied(value=self.instance.recipient, error=None)
            self.server = BaseFied(value=self.instance.server, error=None)
            self.ssl = BaseFied(value=self.instance.ssl, error=None)
            self.auth = BaseFied(value=self.instance.auth, error=None)

            fail_report = self.instance.fail_report
            self.fail_report = BaseFied(value=("" if not fail_report else fail_report), error=None)

            password = base64.decodestring(self.instance.password)
            self.password = BaseFied(value=password, error=None)
            self.disabled = BaseFied(value=str(self.instance.disabled), error=None)
        else:
            self.__setparam()

    def __setparam(self):
        data = self.post if self.post else self.get
        for key,default in self.PARAM_LIST.items():
            if data:
                obj = BaseFied(value=data.get(key, default), error=None)
            elif self.instance:
                obj = BaseFied(value=getattr(self.instance, key), error=None)
            else:
                obj = BaseFied(value=default, error=None)
            setattr(self,key,obj)
        if data.get("mailbox",""):
            self.mailbox = BaseFied(value=data["mailbox"], error=None)
            obj = Mailbox.objects.filter(mailbox=data["mailbox"]).first()
            mailbox_id = obj.id if obj else 0
            self.mailbox_id = BaseFied(value=mailbox_id, error=None)

        if not str(self.account.value).strip():
            self.account.value = ""
            self.server.value = ""
            self.password.value = ""

    def is_valid(self):
        self.__check()
        return self.__valid

    def __check(self):
        if not self.instance:
            if not validators.check_email_ordomain(u"{}".format(self.mailbox.value)):
                self.__valid = False
                self.mailbox.set_error(u"邮箱格式不正确")

        if self.account.value:
            if not validators.check_email_ordomain(u"{}".format(self.account.value)):
                self.__valid = False
                self.account.set_error(u"邮箱格式不正确")

        if self.recipient.value:
            if not validators.check_email_ordomain(u"{}".format(self.recipient.value)):
                self.__valid = False
                self.recipient.set_error(u"邮箱格式不正确")

        if not self.mailbox_id.value or int(self.mailbox_id.value) <= 0 :
            self.__valid = False
            self.mailbox.set_error(u"无效的本地邮箱帐号")
        return self.__valid

    def save(self):
        password = base64.encodestring(self.password.value)

        if self.instance:
            obj = self.instance
            obj.mailbox_id=u"{}".format(self.mailbox_id.value)
            obj.mailbox=u"{}".format(self.mailbox.value)
            obj.account=u"{}".format(self.account.value)
            obj.recipient=u"{}".format(self.recipient.value)
            obj.server=u"{}".format(self.server.value)
            obj.password=u"{}".format(password)

            obj.ssl=u"{}".format(self.ssl.value)
            obj.auth=u"{}".format(self.auth.value)
            obj.fail_report=u"{}".format(self.fail_report.value)
            obj.disabled=self.disabled.value
            obj.save()
        else:
            PostTransfer.objects.create(
                mailbox_id=u"{}".format(self.mailbox_id.value),
                mailbox=u"{}".format(self.mailbox.value),
                account=u"{}".format(self.account.value),
                recipient=u"{}".format(self.recipient.value),
                server=u"{}".format(self.server.value),
                password=u"{}".format(password),
                ssl=u"{}".format(self.ssl.value),
                auth=u"{}".format(self.auth.value),
                fail_report=u"{}".format(self.fail_report.value),
                disabled=self.disabled.value
            )

    @property
    def mailboxLists(self):
        return Mailbox.objects.all()
