# -*- coding: utf-8 -*-
#
import json
import time
import datetime
from IPy import IP

from django import forms
from lib.forms import BaseFied, DotDict
from app.core.models import Mailbox, Domain, CoreAlias, DomainAttr
from app.fail2ban.models import Fail2Ban, Fail2BanTrust, Fail2BanBlock
from django.utils.translation import ugettext_lazy as _

from lib.tools import fail2ban_ip, get_redis_connection
from lib.validators import check_ip

def clear_fail2ban_cache():
    redis = get_redis_connection()
    for keyname in redis.keys("fail2ban_cache*") :
        redis.delete(keyname)

class BanRuleForm(DotDict):

    PARAM_LIST = dict((
            (u'name',u''),
            (u'internal',u'5'),
            (u'block_fail',u'10'),
            (u'block_unexists',u'10'),
            (u'block_minute',u'60'),
            (u'disabled', u'-1'),
    ))

    PROTO_LIST = {
            "all"       :       "proto_all",
            "smtp"      :       "proto_smtp",
            "smtps"     :       "proto_smtps",
            "imap"      :       "proto_imap",
            "imaps"     :       "proto_imaps",
            "pop"       :       "proto_pop",
            "pops"      :       "proto_pops",
    }
    PROTO_LIST2 = dict((v,k) for k,v in PROTO_LIST.iteritems())

    def __init__(self, instance=None, get=None, post=None):
        self.instance = instance
        self.get = get or {}
        self.post = post or {}
        self.__initialize()
        self.__valid = True

    def __initialize(self):
        if self.post or (self.get and not self.instance):
            self.__setparam()
        elif self.instance:
            self.name = BaseFied(value=self.instance.name, error=None)
            self.internal = BaseFied(value=self.instance.internal, error=None)
            self.block_fail = BaseFied(value=self.instance.block_fail, error=None)
            self.block_unexists = BaseFied(value=self.instance.block_unexists, error=None)
            self.block_minute = BaseFied(value=self.instance.block_minute, error=None)
            self.update_time = BaseFied(value=self.instance.update_time, error=None)
            self.disabled = BaseFied(value=str(self.instance.disabled), error=None)

            proto_list = self.instance.proto.split(",")
            for p in proto_list:
                if not p in self.PROTO_LIST:
                    continue
                name = self.PROTO_LIST[p]
                setattr(self, name, BaseFied(value=p, error=None))
        else:
            self.__setparam()

    def __setparam(self):
        #清理掉前面的值
        for name in self.PROTO_LIST2.keys():
            if hasattr(self, name):
                delattr(self, name)
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
            for name,value in self.PROTO_LIST2.items():
                if name in data:
                    obj = BaseFied(value=value, error=None)
                    setattr(self,name,obj)

    def is_valid(self):
        self.__check()
        return self.__valid

    def __check(self):
        if int(self.internal.value) <= 0:
            self.internal.set_error(_(u"无效的时间间隔"))
            self.__valid = False
            return self.__valid
        if int(self.block_minute.value) <= 0:
            self.block_minute.set_error(_(u"屏蔽时间必须大于0"))
            self.__valid = False
            return self.__valid
        if int(self.block_fail.value) <= 0:
            self.block_fail.set_error(_(u"屏蔽时间必须大于0"))
            self.__valid = False
            return self.__valid
        if int(self.block_unexists.value) <= 0:
            self.block_unexists.set_error(_(u"屏蔽时间必须大于0"))
            self.__valid = False
            return self.__valid
        return self.__valid

    def save(self):
        proto_list = []
        for name,value in self.PROTO_LIST2.iteritems():
            if hasattr(self, name):
                proto_list.append(value)
        proto = u",".join(proto_list)
        update_time = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.instance:
            obj = self.instance
            obj.name=u"{}".format(self.name.value)
            obj.proto=u"{}".format(proto)
            obj.internal=u"{}".format(self.internal.value)
            obj.block_fail=u"{}".format(self.block_fail.value)
            obj.block_unexists=u"{}".format(self.block_unexists.value)
            obj.block_minute=u"{}".format(self.block_minute.value)
            obj.update_time=u"{}".format(update_time)
            obj.disabled=self.disabled.value
            obj.save()
        else:
            Fail2Ban.objects.create(
                name=u"{}".format(self.name.value),
                proto=u"{}".format(proto),
                internal=u"{}".format(self.internal.value),
                block_fail=u"{}".format(self.block_fail.value),
                block_unexists=u"{}".format(self.block_unexists.value),
                block_minute=u"{}".format(self.block_minute.value),
                update_time=u"{}".format(update_time),
                disabled=self.disabled.value
            )
        clear_fail2ban_cache()

class BanWhiteListForm(DotDict):

    PARAM_LIST = dict((
            (u'ip', u''),
            (u'name',u''),
            (u'disabled',u'-1'),
        ))

    def __init__(self, instance=None, get=None, post=None):
        self.instance = instance
        self.get = get or {}
        self.post = post or {}
        self.__initialize()
        self.__valid = True

    def __initialize(self):
        if self.post or (self.get and not self.instance):
            self.__setparam()
        elif self.instance:
            self.ip = BaseFied(value=self.instance.ip, error=None)
            self.name = BaseFied(value=self.instance.name, error=None)
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

    def is_valid(self):
        self.__check()
        return self.__valid

    def __check(self):
        try:
            ip = IP(self.ip.value)
        except:
            self.ip.set_error("无效的IP地址格式")
            self.__valid = False
            return self.__valid
        return self.__valid

    def save(self):
        if self.instance:
            obj = self.instance
            obj.ip=u"{}".format(self.ip.value)
            obj.name=u"{}".format(self.name.value)
            obj.disabled=self.disabled.value
            obj.save()
        else:
            Fail2BanTrust.objects.create(
                ip=u"{}".format(self.ip.value),
                name=u"{}".format(self.name.value),
                disabled=self.disabled.value
            )
        clear_fail2ban_cache()

class BanBlockListForm(DotDict):

    PARAM_LIST = dict((
            (u'ip', u''),
            (u'name',u''),
            (u'expire_time',u'0'),
            (u'update_time',u''),
            (u'disabled', u'-1'),
        ))

    def __init__(self, instance=None, get=None, post=None):
        self.instance = instance
        self.get = get or {}
        self.post = post or {}
        self.__initialize()
        self.__valid = True

    def __initialize(self):
        if self.post or (self.get and not self.instance):
            self.__setparam()
        elif self.instance:
            self.ip = BaseFied(value=self.instance.ip, error=None)
            self.name = BaseFied(value=self.instance.name, error=None)
            self.update_time = BaseFied(value=self.instance.update_time, error=None)
            self.disabled = BaseFied(value=str(self.instance.disabled), error=None)
            expire_time = self.instance.expire_time
            t_tuple = time.localtime(int(expire_time))
            self.expire_time = BaseFied(value=time.strftime('%Y-%m-%d %H:%M:%S',t_tuple), error=None)
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

    def is_valid(self):
        self.__check()
        return self.__valid

    def __check(self):
        try:
            ip = IP(self.ip.value)
        except:
            self.ip.set_error("无效的IP地址格式")
            self.__valid = False
            return self.__valid
        try:
            t_tuple = datetime.datetime.strptime(self.expire_time.value,'%Y-%m-%d %H:%M:%S').timetuple()
            expire = int(time.mktime(t_tuple))
            now = time.time()
            if expire <= now:
                self.expire_time.set_error(_(u"必须选择一个未来时间"))
                self.__valid = False
        except Exception,err:
            self.expire_time.set_error(_(u"无效的时间参数"))
            self.__valid = False
            print "err  :  ",err
        return self.__valid

    def save(self):
        t_tuple = datetime.datetime.strptime(self.expire_time.value,'%Y-%m-%d %H:%M:%S').timetuple()
        expire = int(time.mktime(t_tuple))
        update_time = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.instance:
            obj = self.instance
            obj.ip=u"{}".format(self.ip.value)
            obj.name=u"{}".format(self.name.value)
            obj.expire_time=u"{}".format(expire)
            obj.update_time=u"{}".format(update_time)
            obj.disabled=self.disabled.value
            obj.save()
        else:
            Fail2BanBlock.objects.create(
                ip=u"{}".format(self.ip.value),
                name=u"{}".format(self.name.value),
                expire_time=u"{}".format(expire),
                update_time=u"{}".format(update_time),
                disabled=self.disabled.value
            )
        clear_fail2ban_cache()

    def get_expire_time(self):
        return self.expire_time.value
