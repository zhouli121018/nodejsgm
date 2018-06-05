# -*- coding: utf-8 -*-
#
import re
import hashlib
from passlib.hash import md5_crypt
from django.utils.translation import ugettext_lazy as _

from app.distribute.tools import proxy_server_redis
from app.distribute.models import ProxyServerConfig, ProxyServerList, ProxyAccountMove, ProxyAccount
from app.core.models import Mailbox
from lib.forms import BaseFormField, BaseFieldFormat
from lib.validators import check_ip, check_email


class ProxyServerConfigForm(object):

    open = False

    def __init__(self, get=None, post=None, instance=None):
        self.__get = get or {}
        self.__post = post
        self.__valid = True
        self.__instance = instance
        self.__init()

    # -------- field property -------------
    config_data = property(fget=lambda self: self.__form.config_data, fset=None, fdel=None, doc=None)
    pwd = property(fget=lambda self: self.__form.pwd, fset=None, fdel=None, doc=None)
    # 模型
    instance = property(fget=lambda self: self.__instance, fset=None, fdel=None, doc=None)

    def is_valid(self):
        self.__check()
        return self.__valid

    def save(self):
        if self.__instance is not None:
            obj = self.__instance
            obj.config_data=self.config_data.value

            objMd5 = hashlib.md5()
            objMd5.update(self.pwd.value)
            obj.pwd=objMd5.hexdigest()

            obj.save()

            proxy_server_redis("proxy_server_config")

    def __check(self):
        pwd = self.pwd.value
        if len(pwd)<8 or len(pwd)>20:
            self.__form.pwd = self.__form.pwd._replace(error=_(u"授权密码长度不能少于8位或者大于20位！"))
            self.__valid = False

        if not ( re.search(r"[A-Z]+", pwd) and re.search(r"[a-z]+", pwd) and re.search(r"[0-9]+", pwd) ):
            self.__form.pwd = self.__form.pwd._replace(error=_(u"授权密码必须同时包含大小写字符和数字！"))
            self.__valid = False

    def __init(self):
        if self.__get.get("open", ""):
            self.open = True

        self.__form = BaseFormField()
        if self.__post is not None:
            self.__form.config_data = BaseFieldFormat(value=self.__post.get("config_data", ""), error=None)
            self.__form.pwd = BaseFieldFormat(value=self.__post.get("pwd", "").strip(), error=None)
        else:
            self.__form.config_data = BaseFieldFormat(value=self.__instance.config_data, error=None)
            self.__form.pwd = BaseFieldFormat(value="", error=None)


class ProxyServerListForm(object):

    def __init__(self, get=None, post=None, instance=None):
        self.__get = get
        self.__post = post
        self.__valid = True
        self.__instance = instance
        self.__init()

    # -------- field property -------------
    server_name = property(fget=lambda self: self.__form.server_name, fset=None, fdel=None, doc=None)
    server_ip = property(fget=lambda self: self.__form.server_ip, fset=None, fdel=None, doc=None)
    # 模型
    instance = property(fget=lambda self: self.__instance, fset=None, fdel=None, doc=None)

    def is_valid(self):
        self.__check()
        return self.__valid

    def save(self):
        if self.__instance is None:
            ProxyServerList.objects.create(server_name=self.server_name.value, server_ip=self.server_ip.value)
            proxy_server_redis("proxy_server_list")
        else:
            obj = self.__instance
            obj.server_name=self.server_name.value
            obj.server_ip=self.server_ip.value
            obj.save()
            proxy_server_redis("proxy_server_list")

    def __check(self):

        if not self.server_name.value:
            self.__form.server_name = self.__form.server_name._replace(error=_(u"请填写服务器名称！"))
            self.__valid = False

        if not check_ip(self.server_ip.value):
            self.__form.server_ip = self.__form.server_ip._replace(error=_(u"请输入合法的服务器IP！"))
            self.__valid = False

    def __init(self):
        self.__form = BaseFormField()
        if self.__post is not None:
            self.__form.server_name = BaseFieldFormat(value=self.__post.get("server_name", "").strip(), error=None)
            self.__form.server_ip = BaseFieldFormat(value=self.__post.get("server_ip", "").strip(), error=None)
        else:
            if self.__instance is None:
                self.__form.server_name = BaseFieldFormat(value="", error=None)
                self.__form.server_ip = BaseFieldFormat(value="", error=None)
            else:
                self.__form.server_name = BaseFieldFormat(value=self.__instance.server_name, error=None)
                self.__form.server_ip = BaseFieldFormat(value=self.__instance.server_ip, error=None)


class ProxyAccountMoveForm(object):

    def __init__(self, get=None, post=None, instance=None):
        self.__get = get
        self.__post = post
        self.__valid = True
        self.__instance = instance
        self.__init()

    # -------- field property -------------
    mailbox = property(fget=lambda self: self.__form.mailbox, fset=None, fdel=None, doc=None)
    target_server = property(fget=lambda self: self.__form.target_server, fset=None, fdel=None, doc=None)
    sync_mail = property(fget=lambda self: self.__form.sync_mail, fset=None, fdel=None, doc=None)
    # 模型
    instance = property(fget=lambda self: self.__instance, fset=None, fdel=None, doc=None)

    def is_valid(self):
        self.__check()
        return self.__valid

    def save(self):
        if self.__instance is None:
            ProxyAccountMove.objects.create(
                acct_id = self.proxy_account.pk,
                mailbox_id=self.proxy_account.mailbox_id, mailbox=self.mailbox.value,
                from_server=self.proxy_account.acct_server, from_ip=self.from_ip,
                target_server=self.target_server.value, target_ip=self.target_server_obj.server_ip,
                sync_mail=self.sync_mail.value,
                move_type="to", status="init"
            )
        else:
            obj = self.__instance
            obj.sync_mail=self.sync_mail.value
            obj.save()

    def __check(self):
        if self.__instance is None:

            # if not check_email(self.mailbox.value):
            #     self.__form.mailbox = self.__form.mailbox._replace(error=_(u"邮箱格式错误！"))
            #     self.__valid = False

            if not self.mailbox.value:
                self.__form.mailbox = self.__form.mailbox._replace(error=_(u"请选择邮箱！"))
                self.__valid = False
            elif not Mailbox.objects.filter(mailbox=self.mailbox.value).exists():
                self.__form.mailbox = self.__form.mailbox._replace(error=_(u"邮箱已不存在, 请重新选择！"))
                self.__valid = False
            elif ProxyAccountMove.objects.filter(mailbox=self.mailbox.value).exists():
                self.__form.mailbox = self.__form.mailbox._replace(error=_(u"迁移邮箱已存在, 请重新选择！"))
                self.__valid = False

            if not ProxyServerList.objects.filter(pk=self.target_server.value).exists():
                self.__form.target_server = self.__form.target_server._replace(error=_(u"目标服务器不存在，请重新选择！"))
                self.__valid = False

    def __init(self):
        self.__form = BaseFormField()
        if self.__post is not None:
            target_server = self.__post.get("target_server", "")
            self.__form.mailbox = BaseFieldFormat(value=self.__post.get("mailbox", "").strip(), error=None)
            self.__form.target_server = BaseFieldFormat(value=target_server and int(target_server) or 0, error=None)
            self.__form.sync_mail = BaseFieldFormat(value=self.__post.get("sync_mail", "") == "1" and True or False, error=None)
        else:
            if self.__instance is None:
                self.__form.mailbox = BaseFieldFormat(value="", error=None)
                self.__form.target_server = BaseFieldFormat(value=0, error=None)
                self.__form.sync_mail = BaseFieldFormat(value=False, error=None)
            else:
                self.__form.mailbox = BaseFieldFormat(value=self.__instance.mailbox, error=None)
                self.__form.target_server = BaseFieldFormat(value=self.__instance.target_server, error=None)
                self.__form.sync_mail = BaseFieldFormat(value=self.__instance.sync_mail, error=None)

    @property
    def target_server_obj(self):
        return ProxyServerList.objects.filter(pk=self.target_server.value).first()

    @property
    def from_ip(self):
        obj = ProxyServerList.objects.filter(id=self.proxy_account.acct_server).first()
        return obj and obj.server_ip or ""

    @property
    def proxy_account(self):
        return ProxyAccount.objects.filter(mailbox=self.mailbox.value).first()

    @property
    def mailboxLists(self):
        return Mailbox.objects.all()

    @property
    def target_servers(self):
        local_ip = ProxyServerConfig.local_ip().config_data
        return ProxyServerList.objects.exclude(server_ip=local_ip)
