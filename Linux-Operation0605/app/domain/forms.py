# -*- coding: utf-8 -*-
#
import json
from lib.forms import BaseFied, BaseFieldFormatExt, DotDict, BaseCfilterActionFied, BaseCfilterOptionFied
from app.core.models import Mailbox, Domain, CoreAlias, DomainAttr, Department, CoreConfig, CoreMonitor, CoreWhitelist
from app.domain.models import Signature, SecretMail
from django.db.models import Sum,Count

from lib import validators
from lib.formats import dict_compatibility
from lib.tools import clear_redis_cache

from django_redis import get_redis_connection
from django.utils.translation import ugettext_lazy as _

import base64
import time
import copy
import constants
import chardet

from app.core.constants import MAILBOX_SEND_PERMIT, MAILBOX_RECV_PERMIT


# 转换字符串为 unicode
def get_unicode(string) :
    st = type(string)
    if st.__name__ == 'unicode' :
        return string
    if not isinstance(string,str):
        string = str( string )
    charset = chardet.detect(string)['encoding']
    if not charset:
        return string.decode("utf-8","ignore")
    return string.decode(charset)

def get_string(code):
    if isinstance(code,unicode):
        return code.encode('utf-8','ignore')
    return str(code)


#域名配置的基类
class DomainForm(DotDict):

    PARAM_LIST = {}
    PARAM_TYPE = {}

    def __init__(self, domain_id, get=None, post=None):
        self.domain_id = BaseFied(value=domain_id, error=None)
        self.get = get or {}
        self.post = post or {}

        self.valid = True
        self.initialize()

    def initialize(self):
        self.initBasicParams()
        self.initPostParams()

    def formatOptionValue(self, key, value):
        if value.lower() == u"on":
            return u"1"
        return value

    def initBasicParams(self):
        for key, default in self.PARAM_LIST.items():
            sys_type = self.PARAM_TYPE[ key ]
            instance = DomainAttr.objects.filter(domain_id=self.domain_id.value,type=sys_type,item=key).first()
            setattr(self,"instance_%s"%key,instance)

            value = instance.value if instance else default
            obj = BaseFied(value=value, error=None)
            setattr(self,key,obj)

    def initPostParams(self):
        self.initPostParamsDefaultNone()

    def initPostParamsDefaultNone(self):
        data = self.post if self.post else self.get
        if "domain_id" in data:
            self.domain_id = BaseFied(value=data["domain_id"], error=None)
        for key,default in self.PARAM_LIST.items():
            if not key in data:
                continue
            value = self.formatOptionValue(key, data[key])
            obj = BaseFied(value=value, error=None)
            setattr(self,key,obj)

    def initPostParamsDefaultDisable(self):
        data = self.post if self.post else self.get
        if "domain_id" in data:
            self.domain_id = BaseFied(value=data["domain_id"], error=None)
        data = self.post if self.post else self.get
        if data:
            self.domain_id = BaseFied(value=data["domain_id"], error=None)
            for key,default in self.PARAM_LIST.items():
                value = self.formatOptionValue(key, data.get(key, u"-1"))
                obj = BaseFied(value=value, error=None)
                setattr(self,key,obj)

    def is_valid(self):
        if not self.domain_id.value:
            self.valid = False
            self.domain_id.set_error(_(u"无效的域名"))
            return self.valid
        self.check()
        return self.valid

    def check(self):
        return self.valid

    def checkSave(self):
        if self.is_valid():
            self.save()

    def paramSave(self):
        for key in self.PARAM_LIST.keys():
            obj = getattr(self,"instance_%s"%key,None)
            value = getattr(self,key).value
            if obj:
                sys_type = self.PARAM_TYPE[ key ]
                obj.domain_id = u"{}".format(self.domain_id.value)
                obj.type = u"{}".format(sys_type)
                obj.item = u"{}".format(key)
                obj.value = u"{}".format(value)
                obj.save()
            else:
                sys_type = self.PARAM_TYPE[ key ]
                DomainAttr.objects.create(
                    domain_id=u"{}".format(self.domain_id.value),
                    type=u"{}".format(sys_type),
                    item=u"{}".format(key),
                    value=u"{}".format(value)
                )
        clear_redis_cache()

    def save(self):
        self.paramSave()

class DomainBasicForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_BASIC_PARAMS_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_BASIC_PARAMS_TYPE)
    STATUS_LIST = dict(constants.DOMAIN_BASIC_STATUS)

    def initialize(self):
        self.initBasicParams()
        self.initPostParams()
        self.initStatus()
        data = self.post if self.post else self.get
        if not data:
            domainDisabled = Domain.objects.filter(id=self.domain_id.value).first()
            domainDisabled = "1" if not domainDisabled else domainDisabled.disabled
            self.domainDisabled = BaseFied(value=str(domainDisabled), error=None)
        else:
            self.domainDisabled = BaseFied(value=str(data.get("domainDisabled", "1")), error=None)

    def initStatus(self):
        statMailbox = Mailbox.objects.filter(domain_id=self.domain_id.value).aggregate(
                            size__count=Count('id'),
                            size__msum=Sum('quota_mailbox'),
                            size__nsum=Sum('quota_netdisk')
                            )
        mailboxUsed = statMailbox["size__count"]
        spaceUsed = statMailbox["size__msum"]
        netdiskUsed = statMailbox["size__nsum"]
        aliasUsed = len(CoreAlias.objects.filter(domain_id=self.domain_id.value).all())

        self.mailboxUsed = BaseFied(value=mailboxUsed, error=None)
        self.aliasUsed = BaseFied(value=aliasUsed, error=None)
        self.spaceUsed = BaseFied(value=spaceUsed, error=None)
        self.netdiskUsed = BaseFied(value=netdiskUsed, error=None)

    def check(self):
        return self.valid

    def save(self):
        obj_domain = Domain.objects.filter(id=self.domain_id.value).first()
        obj_domain.disabled = u"{}".format(self.domainDisabled.value)
        obj_domain.save()
        self.paramSave()

#用户注册
class DomainRegLoginForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_REG_LOGIN_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_REG_LOGIN_TYPE)

    def initPostParams(self):
        self.initPostParamsDefaultDisable()

    def check(self):
        return self.valid

class DomainRegLoginWelcomeForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_REG_LOGIN_WELCOME_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_REG_LOGIN_WELCOME_TYPE)

    def initialize(self):
        self.subject = u""
        self.content = u""
        self.initBasicParams()

        newData = self.post if self.post else self.get
        if "domain_id" in newData:
            self.domain_id = BaseFied(value=newData["domain_id"], error=None)
        try:
            oldData = json.loads(self.cf_welcome_letter.value)
            self.subject = oldData.get(u"subject",u"")
            self.content = oldData.get(u"content",u"")
        except:
            oldData = {}
        if newData:
            self.subject = newData.get(u"subject",u"")
            self.content = newData.get(u"content",u"")
        saveData = json.dumps( {"subject"    :   self.subject, "content": self.content } )
        self.cf_welcome_letter = BaseFied(value=saveData, error=None)

class DomainRegLoginAgreeForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_REG_LOGIN_AGREE_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_REG_LOGIN_AGREE_TYPE)

#收发限制
class DomainSysRecvLimitForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_SYS_RECV_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_SYS_RECV_TYPE)

    SEND_LIMIT_RANGE = dict(MAILBOX_SEND_PERMIT)
    RECV_LIMIT_RANGE = dict(MAILBOX_RECV_PERMIT)

    def initialize(self):
        self.initBasicParams()
        self.initPostParams()
        data = self.post if self.post else self.get
        self.modify_all_limit_send = data.get("modify_all_limit_send", u"-1")
        self.modify_all_limit_recv = data.get("modify_all_limit_recv", u"-1")

    def initPostParams(self):
        self.initPostParamsDefaultDisable()

    def check(self):
        if not self.limit_send.value in self.SEND_LIMIT_RANGE:
            self.limit_send.set_error(_(u"无效的发信权限"))
            self.valid = False
            return self.valid
        if not self.limit_recv.value in self.RECV_LIMIT_RANGE:
            self.limit_recv.set_error(_(u"无效的收信权限"))
            self.valid = False
            return self.valid
        return self.valid

    def save(self):
        self.paramSave()
        if self.modify_all_limit_send == u"1":
            Mailbox.objects.filter(domain_id=self.domain_id.value).update(limit_send=self.limit_send.value)
        if self.modify_all_limit_recv == u"1":
            Mailbox.objects.filter(domain_id=self.domain_id.value).update(limit_recv=self.limit_recv.value)

    @property
    def getLimitSendParams(self):
        return MAILBOX_SEND_PERMIT

    @property
    def getLimitRecvParams(self):
        return MAILBOX_SEND_PERMIT

class DomainSysRecvWhiteListForm(DotDict):

    def __init__(self, domain_id, type=u"send", get=None, post=None):
        self.type = type
        self.domain_id = BaseFied(value=domain_id, error=None)
        self.get = get or {}
        self.post = post or {}

        self.valid = True
        self.initialize()

    @property
    def getSendLimitWhiteList(self):
        lists = CoreWhitelist.objects.filter(type="send", domain_id=self.domain_id.value, mailbox_id=0).all()
        num = 1
        for d in lists:
            yield num, d.id, d.email, str(d.disabled)
            num += 1

    @property
    def getRecvLimitWhiteList(self):
        lists = CoreWhitelist.objects.filter(type="recv", domain_id=self.domain_id.value, mailbox_id=0).all()
        num = 1
        for d in lists:
            yield num, d.id, d.email, str(d.disabled)
            num += 1

    def initialize(self):
        def getPostMailbox(key):
            #从 entry_{{ mailbox }}_id 这种格式中把 mailbox 提取出来
            l = key.split("_")
            l.pop(0)
            flag = l.pop(-1)
            mailbox = "_".join(l)
            return mailbox
        def setPostMailboxData(mailbox, key, value):
            self.mailboxDict.setdefault(mailbox, {})
            self.mailboxDict[mailbox][key] = value
        #enddef

        self.newMailbox = u""
        self.mailboxDict = {}
        self.newMailboxList = []
        data = self.post if self.post else self.get
        if not data:
            return
        newMailbox = data.get("new_mailbox", u"")
        newMailboxList = data.get("new_mailbox_list", u"")
        if newMailbox:
            self.newMailbox = newMailbox
        boxList = newMailboxList.split("|")
        boxList = [box for box in boxList if box.strip()]
        if boxList:
            self.newMailboxList = boxList

        for k,v in data.items():
            if k.startswith("{}_".format(self.type)):
                if k.endswith("_id"):
                    mailbox = getPostMailbox(k)
                    setPostMailboxData(mailbox, "id", v)
                elif k.endswith("_delete"):
                    mailbox = getPostMailbox(k)
                    setPostMailboxData(mailbox, "delete", v)
        for mailbox in self.mailboxDict.keys():
            isDisabled = data.get(u"{}_{}_disabled".format(self.type, mailbox), u"1")
            setPostMailboxData(mailbox, "disabled", isDisabled)

    def is_valid(self):
        if not self.domain_id.value:
            self.valid = False
            self.domain_id.set_error(_(u"无效的域名"))
            return self.valid
        self.check()
        return self.valid

    def check(self):
        return self.valid

    def checkSave(self):
        if self.is_valid():
            self.save()

    def saveNewEmail(self, mailbox):
        if mailbox in self.mailboxDict:
            return
        obj = CoreWhitelist.objects.create(type=self.type, domain_id=self.domain_id.value, mailbox_id=0, email=mailbox)
        obj.save()

    def saveOldEmail(self):
        for mailbox, data in self.mailboxDict.items():
            data = self.mailboxDict[mailbox]
            entry_id = data.get("id", "")
            if not entry_id:
                continue
            obj = CoreWhitelist.objects.filter(id=entry_id).first()
            if not obj:
                continue
            if data.get("delete", u"-1") == u"1":
                obj.delete()
            else:
                obj.disabled = data.get("disabled", "-1")
                obj.save()

    def save(self):
        #先添加新的邮箱
        if self.newMailbox:
            self.saveNewEmail( self.newMailbox )
        for mailbox in self.newMailboxList:
            self.saveNewEmail( mailbox )
        self.saveOldEmail()

#安全设置
class DomainSysSecurityForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_SYS_SECURITY_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_SYS_SECURITY_TYPE)

    def initialize(self):
        self.count = u"0"
        self.timespan = u"0"
        self.initBasicParams()

        newData = self.post if self.post else self.get
        if "domain_id" in newData:
            self.domain_id = BaseFied(value=newData["domain_id"], error=None)
        try:
            oldData = json.loads(self.cf_def_safe_login.value)
            self.count = oldData.get(u"count",u"0")
            self.timespan = oldData.get(u"timespan",u"0")
        except:
            oldData = {}
        if newData:
            for key,default in self.PARAM_LIST.items():
                value = self.formatOptionValue(key, newData.get(key, u"-1"))
                obj = BaseFied(value=value, error=None)
                setattr(self,key,obj)
            self.count = newData.get(u"count",u"0")
            self.timespan = newData.get(u"timespan",u"0")
        saveData = json.dumps( { "count": self.count,    "timespan": self.timespan } )
        self.cf_def_safe_login = BaseFied(value=saveData, error=None)

class DomainSysSecurityPasswordForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_SYS_SECURITY_PWD_VALUES)
    PARAM_TYPE = dict(constants.DOMAIN_SYS_SECURITY_PWD_TYPE)

    def initialize(self):
        self.subject = u""
        self.content = u""
        self.initBasicParams()

        newData = self.post if self.post else self.get
        if "domain_id" in newData:
            self.domain_id = BaseFied(value=newData["domain_id"], error=None)

        try:
            oldData = json.loads(self.cf_def_login_limit_mail.value)
            self.subject = oldData.get(u"subject",u"")
            self.content = oldData.get(u"content",u"")
        except:
            oldData = {}
        if newData:
            self.subject = newData.get(u"subject",u"")
            self.content = newData.get(u"content",u"")
        saveData = json.dumps( {"subject"    :   self.subject, "content": self.content } )
        self.cf_def_login_limit_mail = BaseFied(value=saveData, error=None)

#密码规则
class DomainSysPasswordForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_SYS_PASSWORD_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_SYS_PASSWORD_TYPE)

    PARAM_TYPE_LIMIT = constants.DOMAIN_SYS_PASSWORD_TYPE_LIMIT
    PARAM_LEN_LIMIT = constants.DOMAIN_SYS_PASSWORD_LEN_LIMIT

    PRAAM_RULE_VALUE = dict(constants.DOMAIN_SYS_PASSWORD_RULE_VALUE)
    PARAM_RULE_LIMIT = dict(constants.DOMAIN_SYS_PASSWORD_RULE_LIMIT)

    def initialize(self):
        self.initBasicParams()
        newData = self.post if self.post else self.get
        if "domain_id" in newData:
            self.domain_id = BaseFied(value=newData["domain_id"], error=None)

        try:
            oldData = json.loads(self.cf_pwd_rule.value)
        except:
            oldData = {}
        oldData = {} if not isinstance(oldData, dict) else oldData
        for name, param in self.PRAAM_RULE_VALUE.items():
            default = self.PARAM_RULE_LIMIT[param]
            setattr(self, name, oldData.get(param, default))
        if newData:
            for key,default in self.PARAM_LIST.items():
                value = self.formatOptionValue(key, newData.get(key, u"-1"))
                obj = BaseFied(value=value, error=None)
                setattr(self,key,obj)
            for name, param in self.PRAAM_RULE_VALUE.items():
                setattr(self, name, newData.get(param, u"-1"))
        saveData = {}
        for name, param in self.PRAAM_RULE_VALUE.items():
            saveData[param] = getattr(self, name)
        self.cf_pwd_rule = BaseFied(value=json.dumps(saveData), error=None)

#第三方对接
class DomainSysInterfaceForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_SYS_INTERFACE_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_SYS_INTERFACE_TYPE)

    def initPostParams(self):
        self.initPostParamsDefaultDisable()

class DomainSysInterfaceAuthApiForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_SYS_INTERFACE_AUTH_API_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_SYS_INTERFACE_AUTH_API_TYPE)

class DomainSysInterfaceIMApiForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_SYS_INTERFACE_IM_API_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_SYS_INTERFACE_IM_API_TYPE)

#杂项设置
class DomainSysOthersForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_SYS_OTHERS_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_SYS_OTHERS_TYPE)

    def initPostParams(self):
        self.initPostParamsDefaultDisable()

class DomainSysOthersCleanForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_SYS_OTHERS_SPACE_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_SYS_OTHERS_SPACE_TYPE)

    def initialize(self):
        self.initBasicParams()
        newData = self.post if self.post else self.get
        if "domain_id" in newData:
            self.domain_id = BaseFied(value=newData["domain_id"], error=None)

        try:
            oldCleanData = json.loads(self.cf_spaceclean.value)
        except:
            oldCleanData = {}
        try:
            oldMailData = json.loads(self.cf_spacemail.value)
        except:
            oldMailData = {}
        oldCleanData = {} if not isinstance(oldCleanData, dict) else oldCleanData
        oldMailData = {} if not isinstance(oldMailData, dict) else oldMailData

        self.general_keep_time  = get_unicode(oldCleanData.get(u"general_keep_time", u"0"))
        self.sent_keep_time     = get_unicode(oldCleanData.get(u"sent_keep_time", u"0"))
        self.spam_keep_time     = get_unicode(oldCleanData.get(u"spam_keep_time", u"0"))
        self.trash_keep_time    = get_unicode(oldCleanData.get(u"trash_keep_time", u"0"))

        self.subject = oldMailData.get(u"subject", u"")
        self.content = oldMailData.get(u"content", u"")
        self.warn_rate=get_unicode(oldMailData.get(u"warn_rate", u"85"))
        if newData:
            self.general_keep_time  = get_unicode(newData.get(u"general_keep_time", u"0"))
            self.sent_keep_time     = get_unicode(newData.get(u"sent_keep_time", u"0"))
            self.spam_keep_time     = get_unicode(newData.get(u"spam_keep_time", u"0"))
            self.trash_keep_time    = get_unicode(newData.get(u"trash_keep_time", u"0"))

            self.subject = newData.get(u"subject", u"")
            self.content = newData.get(u"content", u"")
            self.warn_rate=get_unicode(newData.get(u"warn_rate", u"85"))

        saveCleanData = {
            u"general_keep_time"     :   self.general_keep_time,
            u"sent_keep_time"        :   self.sent_keep_time,
            u"spam_keep_time"        :   self.spam_keep_time,
            u"trash_keep_time"       :   self.trash_keep_time,
        }
        saveMailData = {
            u"subject"     :   self.subject,
            u"content"     :   self.content,
            u"warn_rate"   :   self.warn_rate,
        }
        self.cf_spaceclean = BaseFied(value=json.dumps(saveCleanData), error=None)
        self.cf_spacemail = BaseFied(value=json.dumps(saveMailData), error=None)

class DomainSysOthersAttachForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_SYS_OTHERS_ATTACH_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_SYS_OTHERS_ATTACH_TYPE)

class DomainSignDomainForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_SIGN_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_SIGN_TYPE)

    def initialize(self):
        self.initBasicParams()
        newData = self.post if self.post else self.get
        if "domain_id" in newData:
            self.domain_id = BaseFied(value=newData["domain_id"], error=None)
        try:
            oldData = json.loads(self.cf_domain_signature.value)
        except:
            oldData = {}
        oldData = {} if not isinstance(oldData, dict) else oldData
        self.content_html = oldData.get(u"html",u"")
        if self.content_html and u"new" in oldData:
            self.content_html = base64.decodestring(self.content_html)
        self.content_text = oldData.get(u"text",u"")
        if newData:
            self.content_html               = newData.get(u"content_html", u"")
            self.content_text               = newData.get(u"content_text", u"-1")
        saveData = {
            u"html"         :   get_unicode(base64.encodestring(get_string(self.content_html))),
            u"text"         :   self.content_text,
            u"new"          :   u"1",       #针对老版本的兼容标记
        }
        self.cf_domain_signature = BaseFied(value=json.dumps(saveData), error=None)

class DomainSignPersonalForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_SIGN_PERSONAL_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_SIGN_PERSONAL_TYPE)

    PARAM_LIST_DEFAULT = dict(constants.DOMAIN_SIGN_PERSONAL_VALUE_DEFAULT)

    def initialize(self):
        self.initBasicParams()
        newData = self.post if self.post else self.get
        if "domain_id" in newData:
            self.domain_id = BaseFied(value=newData["domain_id"], error=None)

        try:
            oldData = json.loads(self.cf_personal_sign.value)
        except:
            oldData = {}
        oldData = {} if not isinstance(oldData, dict) else oldData
        for name, default in self.PARAM_LIST_DEFAULT.items():
            setattr(self, name, oldData.get(name, default) )
        if self.personal_sign_templ:
            self.personal_sign_templ = get_unicode(base64.decodestring(get_string(self.personal_sign_templ)))
        if newData:
            self.personal_sign_new          = get_unicode(newData.get(u"personal_sign_new", u"-1"))
            self.personal_sign_forward     = get_unicode(newData.get(u"personal_sign_forward", u"-1"))
            self.personal_sign_auto        = get_unicode(newData.get(u"personal_sign_auto", u"-1"))
            self.personal_sign_templ       = get_unicode(newData.get(u"content_html", u""))
        saveData = {
            u"personal_sign_new"         :   self.personal_sign_new,
            u"personal_sign_forward"    :   self.personal_sign_forward,
            u"personal_sign_auto"        :   self.personal_sign_auto,
            u"personal_sign_templ"       :   get_unicode(base64.encodestring(get_string(self.personal_sign_templ))),
        }
        self.cf_personal_sign = BaseFied(value=json.dumps(saveData), error=None)

    def applyAll(self):
        pass

class DomainModuleHomeForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_MODULE_HOME_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_MODULE_HOME_TYPE)

    def initPostParams(self):
        self.initPostParamsDefaultDisable()

class DomainModuleMailForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_MODULE_MAIL_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_MODULE_MAIL_TYPE)

    def initPostParams(self):
        self.initPostParamsDefaultDisable()

class DomainModuleSetForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_MODULE_SET_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_MODULE_SET_TYPE)

    def initialize(self):
        self.initBasicParams()
        self.initPostParamsDefaultDisable()
        data = self.post if self.post else self.get
        #sw_userbwlist对应的是core_domain的userbwlist列，特殊处理之
        if not data:
            domainObj = Domain.objects.filter(id=self.domain_id.value).first()
            sw_userbwlist = "-1" if not domainObj else domainObj.userbwlist
            self.sw_userbwlist = BaseFied(value=get_unicode(sw_userbwlist), error=None)
        else:
            self.sw_userbwlist = BaseFied(value=get_unicode(data.get("sw_userbwlist", "-1")), error=None)

    def check(self):
        return self.valid

    def save(self):
        domainObj = Domain.objects.filter(id=self.domain_id.value).first()
        domainObj.userbwlist = u"{}".format(self.sw_userbwlist.value)
        domainObj.save()
        self.paramSave()

class DomainModuleOtherForm(DomainForm):

    PARAM_LIST = dict(constants.DOMAIN_MODULE_OTHER_VALUE)
    PARAM_TYPE = dict(constants.DOMAIN_MODULE_OTHER_TYPE)

    def initPostParams(self):
        self.initPostParamsDefaultDisable()

#密级管理
class DomainSecretForm(DotDict):

    def __init__(self, get=None, post=None):
        self.get = get or {}
        self.post = post or {}

        self.error = u""
        self.action = u""

        self.grade = constants.DOMAIN_SECRET_GRADE_1
        self.addList = []
        self.delList = []
        self.valid = True
        self.initialize()

    def initialize(self):
        data = self.post if self.post else self.get
        if data:
            self.action = data.get(u"action", u"")
        self.grade = data.get(u"grade", constants.DOMAIN_SECRET_GRADE_1)

        if self.action == u"new":
            boxList = data.get(u"mailbox", "")
            boxList = [box.strip() for box in boxList.split("|") if box.strip()]
            self.addList = boxList
        if self.action == u"del":
            idList = data.get(u"idlist", "")
            idList = [box.strip() for box in idList.split("|") if box.strip()]
            self.delList = idList

        for grade, name in constants.DOMAIN_SECRET_GRADE_ALL:
            grade_num = len(SecretMail.objects.filter(secret_grade=grade))
            setattr(self, "gradeNum_{}".format( int(grade)+1 ), grade_num)

    @staticmethod
    def getBoxListByGrade(grade):
        dataList = []
        lists = SecretMail.objects.filter(secret_grade=grade)
        for d in lists:
            mailbox_id = d.mailbox_id
            boxObj = Mailbox.objects.filter(id=mailbox_id).first()
            mailbox = u"已删除帐号" if not boxObj else boxObj.mailbox
            dataList.append( {
                "id"        :   d.id,
                "mailbox"  :   mailbox,
            }
            )
        return dataList

    def is_valid(self):
        self.check()
        return self.valid

    def check(self):
        if self.action == u"new":
            for mailbox in self.addList:
                boxObj = Mailbox.objects.filter(mailbox=mailbox).first()
                if not boxObj:
                    self.error = u"邮箱帐号不存在"
                    self.valid = False
                    return self.valid
        elif self.action == u"delete":
            pass
        return self.valid

    def save(self):
        if self.action == u"new":
            for mailbox in self.addList:
                boxObj = Mailbox.objects.filter(mailbox=mailbox).first()
                if not boxObj:
                    continue
                obj = SecretMail.objects.filter(secret_grade=self.grade, mailbox_id=boxObj.id).first()
                if not obj:
                    SecretMail.objects.create(secret_grade=self.grade, mailbox_id=boxObj.id)
        if self.action == u"del":
            for entry_id in self.delList:
                SecretMail.objects.filter(id=entry_id).delete()
