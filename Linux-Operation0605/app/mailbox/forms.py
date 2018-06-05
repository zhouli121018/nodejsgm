# -*- coding: utf-8 -*-
#
import json
import time
import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from app.core.models import Mailbox, MailboxUser
from bootstrapform.templatetags.bootstrap import add_input_classes
from app.core import constants
from app.utils.regex import pure_digits_regex


class MailboxForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _(u"两次输入的密码不一致."),
    }

    password1 = forms.CharField(label=u'登录密码：', widget=forms.PasswordInput,
                                help_text=u'注：密码长度最少为8位，其中必须包括大写字母和小写字母，以及数字！')
    password2 = forms.CharField(label=u'确认密码：', widget=forms.PasswordInput)
    enable_share = forms.BooleanField(label=u'是否打开邮箱共享：', required=False, initial=False)
    limit_pop = forms.BooleanField(label=u'POP功能：', required=False, initial=True)
    limit_imap = forms.BooleanField(label=u'IMAP功能：', required=False, initial=True)
    disabled = forms.BooleanField(label=u'邮箱帐号状态：', required=False, initial=True)
    change_pwd = forms.BooleanField(label=u'登录强制修改密码：', required=False, initial=False)
    pwd_days_time = forms.CharField(label=u'密码有效期：', required=False, widget=forms.TextInput(
        attrs={"class": "datetime", "value": time.strftime('%Y-%m-%d %H:%M:%S')}))

    def __init__(self, domain, *args, **kwargs):
        super(MailboxForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget = forms.TextInput(attrs={
            "placeholder": _(u"邮箱名称"),
        })
        self.domain = domain
        self.domain_str = domain.domain
        self.fields['domain'].required = False
        self.fields['domain_str'].required = False
        self.fields['mailbox'].required = False
        self.fields['name'].widget.attrs.update({'addon': self.domain_str})
        self.fields['quota_mailbox'].widget.attrs.update({'addon': u'MB'})
        self.fields['quota_netdisk'].widget.attrs.update({'addon': u'MB'})
        self.fields['pwd_days'].widget.attrs.update({'addon': u'天'})

        if self.instance.pk:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            s = self.instance.size
            size = s.size if s else 0
            self.fields['quota_mailbox'].widget.attrs.update({'addon': u'MB(已使用{}MB)'.format(size)})
            self.fields['quota_netdisk'].widget.attrs.update({'addon': u'MB(已使用{}MB)'.format(size)})


    def clean_domain(self):
        return self.domain

    def clean_domain_str(self):
        return self.domain_str

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1)<8:
            raise forms.ValidationError(_(u"您的密码必须至少包含8个字符。",))
        if pure_digits_regex(password1):
            raise forms.ValidationError(_(u"您的密码不能完全是数字。", ))
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        # self.instance.username = self.cleaned_data.get('username')
        # password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2

    def clean_limit_imap(self):
        data = self.cleaned_data.get('limit_imap')
        return '-1' if data else '1'

    def clean_disabled(self):
        data = self.cleaned_data.get('limit_disabled')
        return '-1' if data else '1'

    def clean_change_pwd(self):
        data = self.cleaned_data.get('limit_change_pwd')
        return '-1' if data else '1'

    def clean_enable_share(self):
        data = self.cleaned_data.get('limit_enable_share')
        return '-1' if data else '1'

    def clean_mailbox(self):
        data = self.cleaned_data
        return '{}@{}'.format(data.get('name'), self.domain_str)

    def clean_pwd_days_time(self):
        data = self.cleaned_data.get('pwd_days_time')
        return int(time.mktime(time.strptime(data, '%Y-%m-%d %H:%M:%S')))

    class Meta:
        model = Mailbox
        exclude = ['recvsms', 'sys_mailbox', 'first_change_pwd']


class MailboxUserForm(forms.ModelForm):
    oabshow = forms.BooleanField(label=u'通讯录显示：', required=False, initial=True)
    remark = forms.CharField(label=u'备注：', required=False, widget=forms.Textarea(attrs={'rows': '4'}))

    def __init__(self, domain, *args, **kwargs):
        super(MailboxUserForm, self).__init__(*args, **kwargs)
        self.domain = domain
        self.fields['domain'].required = False

    def clean_oabshow(self):
        data = self.cleaned_data.get('oabshow')
        return '1' if data else '-1'

    def clean_domain(self):
        return self.domain

    def save(self, id, commit=True):
        mem = super(MailboxUserForm, self).save(commit=False)
        mem.id = id
        if commit:
            mem.save()
        return mem

    class Meta:
        model = MailboxUser
        exclude = ['id', 'openid', 'wx_id', 'unionid', 'oabshow']
