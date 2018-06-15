#coding=utf-8

import json
import datetime
from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UsernameField
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.utils.text import capfirst

from app.core.models import CoreLoginAreaIp
from lib.IpSearch import IpSearch
from lib.common import get_client_ip
from django.db.models import Q
from lib.pushcrew import pushcrew_notice
from django_redis import get_redis_connection
from lib.ipparse import parse_login_area, split_ip_to_area_title

class CustomizeAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': ''}),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
    )
    captcha = forms.CharField(
        label=_("Captcha"),
        strip=False,
        widget=forms.TextInput(),
    )

    error_messages = {
        'invalid_login': _(
            "请输入正确的用户名和密码.注意大小写."
        ),
        'inactive': _("此帐户无效."),
    }

    error_messages_loginsafe = {
        'invalid_login': _(
            "未授权的异地登录,请使用事先绑定的微信扫码登录！"
        ),
        'inactive': _("此帐户无效."),
    }

    error_messages_loginsafe2 = {
        'invalid_login': _(
            "未授权的异地登录,请使用事先绑定的微信扫码登录！"
        ),
        'inactive': _("此帐户无效."),
    }

    error_messages_disabled = {
        'invalid_login': _(
            "此账户未开通或已被冻结！"
        ),
        'inactive': _("此帐户无效."),
    }

    error_messages_disabled2 = {
        'invalid_login': _(
            "母账户已被冻结，子账户也被冻结！"
        ),
        'inactive': _("此帐户无效."),
    }
    error_messages_captcha = {
        'invalid_login': _(
            "滑动验证失败，请重新验证！"
        ),
        'inactive': _("此帐户无效."),
    }


    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(CustomizeAuthenticationForm, self).__init__(*args, **kwargs)

        # Set the label for the "username" field.
        UserModel = get_user_model()
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        captcha = self.cleaned_data.get('captcha')
        redis = get_redis_connection()
        key = 'captcha:{}'.format(captcha)
        if redis.hget(key, 'res') != 'True':
            raise forms.ValidationError(
                self.error_messages_captcha['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name},
            )
        redis.delete(key)

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            login_ip = get_client_ip(self.request)
            ##### 地区登录保护 #####
            if self.user_cache:
                if self.user_cache.disabled == '1':
                    raise forms.ValidationError(
                        self.error_messages_disabled['invalid_login'],
                        code='invalid_login',
                        params={'username': self.username_field.verbose_name},
                    )
                if self.user_cache.parent and self.user_cache.parent.disabled == '1':
                    raise forms.ValidationError(
                        self.error_messages_disabled2['invalid_login'],
                        code='invalid_login',
                        params={'username': self.username_field.verbose_name},
                    )
                weixin_customer_id = self.user_cache.weixin_customer_id
                customer_id = self.user_cache.id
                ip_search = IpSearch()
                ip_info = ip_search.Find(login_ip)
                login_area1, login_area2 = parse_login_area(ip_info)
                obj, _created = CoreLoginAreaIp.objects.get_or_create(user_id=customer_id)
                is_open = False if _created else obj.is_open
                _exists = CoreLoginAreaIp.objects.filter(
                    Q(user_id=customer_id, ip__icontains=login_ip) |
                    Q(user_id=customer_id, area__icontains=login_area1) |
                    Q(user_id=customer_id, area__icontains=login_area2)
                ).exists()
                if is_open and not _exists:
                    j_area, j_title = split_ip_to_area_title(ip_info)
                    redis.rpush('edm_web_notice_queue', json.dumps(
                        {
                            "type": "1",
                            'customer_id': customer_id,
                            "area": j_title,
                            'point': '',
                            'domain': '',
                            'task': '',
                        }
                    ))
                    if weixin_customer_id:
                        raise forms.ValidationError(
                            self.error_messages_loginsafe['invalid_login'],
                            code='invalid_login',
                            params={'username': self.username_field.verbose_name},
                        )
                    else:
                        raise forms.ValidationError(
                            self.error_messages_loginsafe2['invalid_login'],
                            code='invalid_login',
                            params={'username': self.username_field.verbose_name},
                        )

            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.user_cache.last_ip = login_ip
                self.user_cache.last_login = timezone.now()
                self.user_cache.save(update_fields=['last_ip', 'last_login'])
                agent = self.request.META.get('HTTP_USER_AGENT', None)
                self.user_cache.save_login_log(login_ip, ip_info, agent)
                self.confirm_login_allowed(self.user_cache)

                # 关注用户上线通知
                s = self.user_cache.service()
                if s and s.is_pushcrew:
                    action = "service"
                    title = u"登录提醒"
                    message = u"{}（ID: {}） 于 {} 时间登录平台".format(
                            self.user_cache.company, self.user_cache.id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    pushcrew_notice(action, title, message)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache

