# coding=utf-8
import os
import base64
import time
import datetime
from hashlib import md5
from phpserialize import unserialize
from xxtea import decrypt
from lib.tools import str2datetime

from django.conf import settings
from functools import wraps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import resolve_url
from django.utils.decorators import available_attrs
from django.utils.six.moves.urllib.parse import urlparse


class Licence(object):
    """
    Webmail证书
    """

    def __init__(self, licence_data='', licence_file=''):
        """
        :param licence_data: 证书内容
        :param licence_file: 证书文件
        :return:
        """
        self.licence_data = licence_data if licence_data else open(licence_file, 'r').read()
        self.secret_string = "MY<wbZNZwGYR{CGguskna6([epEquI62yV7k{VlfynhYnpaIoGRLs3OX9TXoCGznJQYZK<mv{G5k)7Ky3GRfvO4RYsrL{7HFVw9(775J{ZS7t6A>}f)]fVKdoOYYez4IjTe5W[SQ]1aA6DzKP33wf)>GzltWtNS<{Pls[ldjtb[Q(jVbQ{Mih>m}0>[5abgCjU>4Tk6{2ycoWT9[wWjFK0K4srWJ1LxUNg]M0cyLMWLvw6O7JqCF[7bnPlCr{dUn"
        self.service_out = False
        self.parse_licence()


    def parse_licence(self):
        raw_info = self._parse_raw_licence(self.licence_data)

        # 取得 Licence 版本信息
        version = self._get_licence_version(raw_info)

        # 分析不同版本的 Licence
        #print "licence version is ",version
        if version == '1.1':
            licence_info = self._parse_info_1_1(raw_info)
        elif version == '1.2':
            licence_info = self._parse_info_1_2(raw_info)
        else:
            licence_info = self._parse_info_1_0(raw_info)

        #检测技术支持服务是否结束
        service_end = licence_info['service_end']
        if service_end and datetime.datetime.now() > service_end:
            self.service_out = True
        #print licence_info
        self.licence_info = licence_info

    # 取得授权信息
    def get_licence_info(self):
        return self.licence_info

    # 解析 Licence 原始信息
    def _parse_raw_licence(self, data):
        seed = md5(self.secret_string).hexdigest()
        data = decrypt(base64.decodestring(data), seed)
        info = unserialize(data)
        return info

    # 取得 Licence 版本信息
    def _get_licence_version(self, raw_info):
        return str(raw_info['version']) if 'version' in raw_info else '1.0'

    # 取得有效的扩展模块
    def get_available_module(self):
        # 试用用户允许使用所有模块
        if self.licence_info['evaluation']:
            return ['all']

        # 如果技术支持服务未过期，则返回所有扩展模块
        if self.service_out:
            return self.licence_info['extra_module']

        # 如技术支持已过期，则筛选出其已权限的扩展模块
        extra_module = []
        for m in self.licence_info['extra_module']:
            if m not in self.licence_info['limit_module']:
                extra_module.append(m)
        return extra_module;

    # #### 分析不同版本的 Licence 信息
    # 1.2
    def _parse_info_1_2(self, raw_info):
        data = {
            'version': '1.2',
            'domain_name': raw_info['domain_name'],
            'organization': raw_info['organization'],
            'evaluation': raw_info['evaluation'],
            'limit_count': raw_info['limit_count'],
            'service_begin': str2datetime(raw_info['service_begin']),
            'service_end': str2datetime(raw_info['service_end']),
            'expires_time': str2datetime(raw_info['expires_time']),
            'extra_module': raw_info['extra_module'],
            'limit_module': raw_info['limit_module'],
            'generate_time': str2datetime(raw_info['generate_time']),
        }
        return data

    # 1.1
    def _parse_info_1_1(self, raw_info):
        data = {
            'domain_name': raw_info['domain'],
            'organization': raw_info['company'],
            'evaluation': raw_info['testing'],
            'limit_count': raw_info['count'],
            'service_begin': '',
            'service_end': '',
            'expires_time': str2datetime(raw_info['expired']),
            'extra_module': raw_info['module'],
            'limit_module': [],
            'generate_time': str2datetime(raw_info['generated']),
        }
        return data;

    # 1.0
    def _parse_info_1_0(self, raw_info):
        data = {
            'domain_name': raw_info['domain'],
            'organization': raw_info['company'],
            'evaluation': raw_info['test_user'],
            'limit_count': raw_info['user_limit'],
            'service_begin': '',
            'service_end': '',
            'expires_time': str2datetime(raw_info['date_expired']),
            'extra_module': [],
            'limit_module': [],
            'generate_time': str2datetime(raw_info['date_register']),
        }
        return data

def licence_validate():
    if os.name == "nt":
        return True
    licence_file = '/usr/local/u-mail/data/www/webmail/licence.dat'
    if not os.path.exists(licence_file):
        return False
    try:
        lic = Licence(licence_file=licence_file)
        info = lic.get_licence_info()
    except Exception,err:
        print "licence error:  ",err
        lines = []
        import traceback
        for line in traceback.format_exc().strip().split('\n') : lines.append('  > ' + line)
        err_msg = '\n'.join(lines)
        print "err_msg:   ",err_msg
        return False

    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    #试用期用户
    try:
        if info['evaluation']:
            from app.core.models import DomainAttr
            value = DomainAttr.getAttrObjValue(domain_id=1,type='system',item='created')
            if not value:
                print "domain_attr has no created flag!!!"
                return False
            start = time.mktime(time.strptime(value,'%Y-%m-%d %H:%M:%S'))
            end = int(start) + 30*24*3600
            end = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(end))
            info["expires_time"] = datetime.datetime.strptime(end,'%Y-%m-%d %H:%M:%S')
            #print "evaluation version start: %s end: %s"%(value, end)
    except Exception,err:
        print "licence trans time error:  ",err
        return False

    #print info
    if info.get("expires_time","") and info["expires_time"].strftime('%Y%m%d%H%M%S')<=now:
        print "invalid licence expires_time:  ",info
        return False
    return True

def licence_passes_test(login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            is_licene = licence_validate()
            is_auth = request.user.is_authenticated()
            if is_licene and is_auth:
                return view_func(request, *args, **kwargs)
            if not is_licene:
                resolved_login_url= "/operation/licence_notify"
            else:
                resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            path = request.build_absolute_uri()
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator

def licence_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = licence_passes_test(
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
