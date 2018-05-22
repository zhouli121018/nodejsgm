# coding=utf-8
from django import forms

from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import UserChangeForm
from models import Customer, CustomerIp, CustomerDomain, CustomerMailbox, Cluster, ClusterIp, IpPool, CUSTOMER_STATUS, \
    RouteRule, CustomerSetting, MyPermission, ColCustomerDomain, CustomerLocalizedSetting
from apps.mail.models import MAIL_SERVERS
import re

CONTENT_TYPE = (
    ('', u'--'),
    ('core.customer', u'客户信息'),
    ('mail.domainblacklist', u'中继发件人域名黑名单'),
    ('mail.senderblacklist', u'发件人关键字黑名单'),
    ('mail.recipientblacklist', u'收件人黑名单'),
    ('mail.subjectkeywordblacklist', u'主题关键字黑名单'),
    ('mail.keywordblacklist', u'内容关键字黑名单'),
    ('mail.customkeywordblacklist', u'中继自动回复关键字'),
    ('mail.attachmentblacklist', u'附件关键字黑名单'),
    ('mail.subjectkeywordwhitelist', u'中继主题白名单'),
    ('mail.relaysenderwhitelist', u'中继发件人白名单'),
    ('mail.recipientwhitelist', u'中继收件人白名单'),
    ('mail.tempsenderblacklist', u'中继临时发件人黑名单'),
    ('mail.invalidsenderwhitelist', u'中继无效地址白名单'),
    ('mail.senderwhitelist', u'网关发件人白名单'),
    ('mail.customersenderblacklist', u'网关发件人黑名单'),
    ('mail.collectrecipientwhitelist', u'网关收件人白名单'),
    ('mail.collectrecipientchecklist', u'网关收件人强制检测名单'),
    ('mail.attachmenttypeblacklist', u'网关小危附件类型'),
    ('mail.spamrptblacklist', u'网关隔离报告收件人黑名单'),
)

class CustomerForm(UserChangeForm):

    class Meta:
        model = Customer
        exclude = ['disabled', 'creater', 'operater', 'operate_time']
        widgets = {
            'service_start': forms.DateInput(attrs={'class': 'dateinput'}),
            'service_end': forms.DateInput(attrs={'class': 'dateinput'}),
            'gateway_service_start': forms.DateInput(attrs={'class': 'dateinput'}),
            'gateway_service_end': forms.DateInput(attrs={'class': 'dateinput'}),
        }

class CustomerMinForm(UserChangeForm):
    class Meta:
        model = Customer
        fields = ['password', 'type', 'contact', 'mobile', 'email', 'emergency_contact', 'emergency_mobile', 'ip_pool']

class CustomerCreateForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ['disabled', 'password', 'last_login', 'creater', 'operater', 'operate_time']
        widgets = {
            'service_start': forms.DateInput(attrs={'class': 'dateinput'}),
            'service_end': forms.DateInput(attrs={'class': 'dateinput'}),
        }


class CustomerIpForm(forms.ModelForm):
    class Meta:
        model = CustomerIp
        exclude = ['customer', 'disabled']


class CustomerDomainForm(forms.ModelForm):
    class Meta:
        model = CustomerDomain
        exclude = ['customer', 'disabled']


class CustomerMailboxForm(forms.ModelForm):
    class Meta:
        model = CustomerMailbox
        exclude = ['customer', 'disabled']


class ColCustomerDomainForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ColCustomerDomainForm, self).__init__(*args, **kwargs)
        self.fields['customer'].widget = forms.HiddenInput()

    def clean_forward_address(self):
        return self.cleaned_data['forward_address'].strip()

    class Meta:
        model = ColCustomerDomain
        exclude = []


class ClusterForm(forms.ModelForm):
    class Meta:
        model = Cluster
        fields = ['name', 'ip', 'port', 'username', 'password', 'api_url', 'description']

    def clean_api_url(self):
        data = self.cleaned_data['api_url']
        if not data:
            data = 'http://{}:10001/state/'.format(self.cleaned_data['ip'])
        return data


class IpSegmentForm(forms.ModelForm):
    ip = forms.CharField(label=u'公网IP段', max_length=100,
                         help_text=u'参考: 202.103.188.188/32. 202.103.199.1/24, 使用保留IP无效.')
    helo = forms.CharField(label=u'helo', max_length=200,
                           help_text=u'支持变量, 如: helo为www{2}-{3}.yourhostname.com, IP为202.103.188.187, helo即: www188-187.yourhostname.com.')

    def clean_ip(self):
        ip = self.cleaned_data['ip']
        r = re.compile(r'^\d+\.\d+\.\d+\.\d+/\d{1,2}$', re.IGNORECASE)
        if not r.search(ip):
            raise forms.ValidationError(u'%s 不是一个合法网段地址' % ip)
        return ip

    def clean_device(self):
        device = self.cleaned_data['device']
        r = re.compile(r'^eth\d$', re.IGNORECASE)
        if not r.search(device):
            raise forms.ValidationError(u'%s 不是一个合法的设备名' % device)
        return device

    class Meta:
        model = ClusterIp
        exclude = ['cluster', 'ip']


class IpPoolForm(forms.ModelForm):
    class Meta:
        model = IpPool
        exclude = []


class CustomerBaseSearchForm(forms.Form):
    username = forms.CharField(label=u'用户/公司', required=False)
    customer_id = forms.IntegerField(label=u'用户id', required=False)
    type = forms.CharField(label=u'类型', required=False, widget=forms.HiddenInput())


class RelayCustomerSearchForm(CustomerBaseSearchForm):
    status = forms.ChoiceField(label=u'中继状态', required=False, choices=CUSTOMER_STATUS)
    ip = forms.CharField(label=u'IP', required=False)
    domain = forms.CharField(label=u'域名', required=False)
    mailbox = forms.CharField(label=u'帐号', required=False)


class CustomerSearchForm(CustomerBaseSearchForm):
    status = forms.ChoiceField(label=u'中继状态', required=False, choices=CUSTOMER_STATUS)
    gateway_status = forms.ChoiceField(label=u'网关状态', required=False, choices=CUSTOMER_STATUS)
    ip = forms.CharField(label=u'IP', required=False)
    domain = forms.CharField(label=u'域名', required=False)
    mailbox = forms.CharField(label=u'帐号', required=False)
    col_domain = forms.CharField(label=u'网关域名', required=False)


class ColCustomerSearchForm(CustomerBaseSearchForm):
    gateway_status = forms.ChoiceField(label=u'网关状态', required=False, choices=CUSTOMER_STATUS)
    col_domain = forms.CharField(label=u'网关域名', required=False)


class RouteRuleForm(forms.ModelForm):
    class Meta:
        model = RouteRule
        exclude = []


class CustomerSettingForm(forms.ModelForm):

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
        exclude = ['customer']


class MyPermissionForm(forms.ModelForm):
    class Meta:
        model = MyPermission
        exclude = ['permission']

    def __init__(self, *args, **kwargs):
        super(MyPermissionForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = MyPermission.objects.filter(parent__isnull=True)


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ['permissions']


class UserForm(UserChangeForm):
    class Meta:
        model = User
        exclude = ['is_staff', 'date_joined', 'last_login', 'is_superuser', 'user_permissions']


class SuperUserForm(UserChangeForm):
    class Meta:
        model = User
        exclude = ['date_joined', 'last_login', 'user_permissions']


class PostfixSearchForm(forms.Form):
    date = forms.DateField(label=u'日期', required=False,
                           widget=forms.DateInput(attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 10}))
    server_id = forms.ChoiceField(label=u'服务器', choices=MAIL_SERVERS, required=True)
    search = forms.CharField(label=u'搜索字段', required=True)


class CustomerLocalizedSettingForm(forms.ModelForm):
    class Meta:
        model = CustomerLocalizedSetting
        exclude = ['customer']

class CustomerSummarySearchForm(forms.Form):
    date_start = forms.DateField(label=u'开始日期', required=False,
                                 widget=forms.DateInput(
                                     attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 12}))
    date_end = forms.DateField(label=u'结束日期', required=False,
                           widget=forms.DateInput(attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 12}))
    username = forms.CharField(label=u'用户/公司', required=False)
    customer_id = forms.IntegerField(label=u'用户id', required=False)
    is_relay_limit = forms.BooleanField(label=u'中继超限', required=False)
    is_collect_limit = forms.BooleanField(label=u'网关超限', required=False)
    is_limit = forms.BooleanField(label=u'超限', required=False)
    is_rid_tmp = forms.BooleanField(label=u'去掉临时信任', required=False)
    is_all = forms.BooleanField(required=False, widget=forms.HiddenInput())

class AuditLogSearchForm(forms.Form):
    content_type = forms.ChoiceField(label=u'类型', choices=CONTENT_TYPE, required=False)
    serach = forms.CharField(label=u'搜索内容', required=False, widget=forms.HiddenInput())
    id = forms.IntegerField(required=False, widget=forms.HiddenInput())

