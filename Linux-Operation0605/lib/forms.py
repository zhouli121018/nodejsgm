# -*- coding: utf-8 -*-
#

from collections import namedtuple

# form 保存字段容器
class BaseFormField(object):
    pass

#  form视图 字段初始化
BaseFormFieldFormat = lambda field_names: namedtuple("BaseFormFieldFormat", field_names)

BaseFieldFormat = BaseFormFieldFormat(['value', 'error'])
BaseFieldFormatExt = BaseFormFieldFormat(['value', 'error', 'extra'])
BaseFieldFormatOption = BaseFormFieldFormat(['id', 'type', 'action', 'value', 'error' ])

class BaseFied(object):

    def __init__(self, value, error=None, is_strip=True):
        self.value = value
        if is_strip and isinstance(value, (basestring, str)):
            self.value = value.strip()
        self.error = error

    def set_error(self, error):
        self.error = error

class BaseCfilterActionFied(object):

    def __init__(self, id, action, field="", value="", sequence=999, error=None,
                 mail_sender="", mail_recipient="", mail_subject="", mail_type="html", mail_content_html="", mail_content_plain="",
                 trans_server="", trans_account="", trans_password="",trans_ssl="", trans_auth="",
                 json_value=None):
        self.id = id
        self.action = action
        self.field = field
        self.value = value
        self.sequence=sequence
        self.error = error
        self.mail_sender = mail_sender
        self.mail_recipient = mail_recipient
        self.mail_subject = mail_subject
        self.mail_type = mail_type
        self.mail_content_html = mail_content_html
        self.mail_content_plain = mail_content_plain

        self.trans_server = trans_server
        self.trans_account = trans_account
        self.trans_password = trans_password
        self.trans_ssl = trans_ssl
        self.trans_auth = trans_auth

        self.json_value = json_value

    def set_error(self, error):
        self.error = error


class BaseCfilterOptionFied(object):

    def __init__(self, id, parent_id="", logic="all", option="", suboption="", action="", value="", childs=None, error=None):
        self.id = id
        self.parent_id = parent_id
        self.logic = logic
        self.option = option
        self.suboption = suboption
        self.action = action
        self.value = value
        if childs is None:
            childs=[]
        self.childs = childs
        self.error = error

    def set_error(self, error):
        self.error = error


class DotDict(dict):
    '''用于操作 dict 对象

    >>> dd = DotDict(a=1, b=2)
    >>> dd.c = 3
    >>> dd
    {'a': 1, 'c': 3, 'b': 2}
    >>> del dd.c
    >>> dd
    {'a': 1, 'b': 2}
    '''

    Fields = tuple()

    def __getitem__(self, name):
        value = dict.__getitem__(self, name)
        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict(value)
        return value

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    __getattr__ = __getitem__
    # __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

#  防止多次提交form视图的装饰器
# 补充一点：必须将表单填写页面的view同时使用@never_cache装饰，因为django默认将所有view都做缓存，当再次进入表单页时，就不会重新生成随机串，导致校验无故失败。。。
from functools import wraps
import random
from django.conf import settings
from django.utils.decorators import available_attrs
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from hashlib import md5

randrange = hasattr(random, 'SystemRandom') and random.SystemRandom().randrange or random.randrange
_MAX_CSRF_KEY = 18446744073709551616L     # 2 << 63

def _get_new_submit_key():
    return md5("%s%s" % (randrange(0, _MAX_CSRF_KEY), settings.SECRET_KEY)).hexdigest()

def anti_resubmit(page_key='', redirect='home'):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            submit_key = '{}_{}_submit'.format(page_key, request.user.id)
            if request.method == "GET":
                request.session[submit_key] = _get_new_submit_key()
                # print 'session:' + request.session.get(submit_key)
            elif request.method == "POST":
                old_key = request.session.get(submit_key, "")
                if old_key == '':
                    return HttpResponseRedirect(reverse(redirect))
                request.session[submit_key] = ""
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


