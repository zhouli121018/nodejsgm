# coding=utf-8

from django import forms
from django.contrib.auth.forms import UserChangeForm
from models import Customer, CustomerSetting, ACTION_TYPE
from captcha.fields import CaptchaField, CaptchaTextInput
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _


class CustomerForm(UserChangeForm):
    class Meta:
        model = Customer
        fields = ['company', 'email', 'contact', 'mobile', 'emergency_contact', 'emergency_mobile', 'password']


class CustomerSettingForm(forms.ModelForm):
    class Meta:
        model = CustomerSetting
        exclude = ['customer']


class CustomerRelaySettingForm(forms.ModelForm):
    class Meta:
        model = CustomerSetting
        fields = ['bounce', 'notice', 'bigmail']


class CustomerCollectSettingForm(forms.ModelForm):

    def clean_spamrpt_sendtime(self):
        data = self.cleaned_data['spamrpt_sendtime']
        b = self.data.get('is_spamrpt_sendtime', '')
        if not b:
            return None
        if b and not data:
            raise forms.ValidationError(u"请设置隔离报告发送时间")
        return data

    class Meta:
        model = CustomerSetting
        exclude = ['customer', 'bounce', 'can_view_mail', 'bigmail', 'notice', 'transfer_max_size', 'replace_sender',
                   'check_autoreply', 'service_notice', 'interval_spamrpt']


class MyAuthenticationForm(AuthenticationForm):
    captcha = CaptchaField()

    def clean(self):
        super(MyAuthenticationForm, self).clean()
        user_cache = self.user_cache
        user_type = user_cache.type
        status = user_cache.status
        gateway_status = user_cache.gateway_status
        if (user_type in ['relay', 'all'] and status != 'disabled') or (
                user_type in ['collect', 'all'] and gateway_status != 'disabled'):
            return self.cleaned_data
        raise forms.ValidationError(
            _(u'密码错误或账户被禁用！'),
            code='invalid_login',
            params={'username': self.username_field.verbose_name},
        )


class OperateLogSearchForm(forms.Form):
    date_start = forms.DateField(label=_(u'开始日期'), required=False,
                                 widget=forms.DateInput(
                                     attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 12}))
    date_end = forms.CharField(label=_(u'结束日期'), required=False,
                               widget=forms.DateInput(
                                   attrs={'class': 'dateinput ', 'readonly': 'readonly', 'size': 12}))
    action = forms.ChoiceField(label=_(u'操作类型'), required=False, choices=ACTION_TYPE)
