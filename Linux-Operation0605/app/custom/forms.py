# -*- coding: utf-8 -*-
#
import json
import time
import datetime

from django import forms
from lib.forms import BaseFied, DotDict
from app.core.models import Mailbox, Domain, DomainAttr
from app.custom.models import CustomKKServerToken

from lib.tools import clear_redis_cache
from django.utils.translation import ugettext_lazy as _

class CustomKKserverForm(DotDict):

    PARAM_LIST = dict((
            (u'server', u''),
            (u'corp', u'0001'),
            (u'service', u''),
            (u'open', u'1'),
            (u'loginurl', u''),
    ))

    def __init__(self, instance=None, get=None, post=None):
        self.instance = instance
        self.get = get or {}
        self.post = post or {}
        self.__initialize()
        self.__valid = True

    def __initialize(self):
        if self.instance:
            value = json.loads(self.instance.value)
            self.server = BaseFied(value=value["server"], error=None)
            self.corp = BaseFied(value=value["corp"], error=None)
            self.service = BaseFied(value=value["service"], error=None)
            self.open = BaseFied(value=str(value.get("open","1")), error=None)
            self.loginurl = BaseFied(value=value.get("loginurl",""), error=None)
        self.__setparam()

    def __setparam(self):
        data = self.post if self.post else self.get
        for key,default in self.PARAM_LIST.items():
            if data:
                obj = BaseFied(value=data.get(key, default), error=None)
                setattr(self,key,obj)
            #设置默认值
            elif not self.instance:
                if key == "loginurl":
                    obj_domain = Domain.objects.all().first()
                    if obj_domain:
                        default = u"http://mail.%s"%(obj_domain.domain)
                obj = BaseFied(value=default, error=None)
                setattr(self,key,obj)

    def is_valid(self):
        self.__check()
        return self.__valid

    def __check(self):
        if not self.server.value.strip():
            self.server.set_error(_(u"无效的服务器参数"))
            self.__valid = False
            return self.__valid
        if not self.corp.value.strip():
            self.corp.set_error(_(u"无效的corp参数"))
            self.__valid = False
            return self.__valid
        if not self.service.value.strip():
            self.service.set_error(_(u"无效的service参数"))
            self.__valid = False
            return self.__valid
        if not self.loginurl.value.strip():
            self.loginurl.set_error(_(u"无效的邮件查看地址"))
            self.__valid = False
            return self.__valid
        return self.__valid

    def save(self):
        value = {
            "server"        :   self.server.value,
            "corp"          :   self.corp.value,
            "service"      :   self.service.value,
            "loginurl"     :   self.loginurl.value,
            "open"          :   self.open.value,
        }
        value = json.dumps( value )
        DomainAttr.saveAttrObjValue(domain_id=0, type="system", item="sw_custom_kkserver_setting", value=value)
        clear_redis_cache()
