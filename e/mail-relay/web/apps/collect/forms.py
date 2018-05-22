# coding=utf-8
from django import forms
from models import ColCustomer, ColCustomerDomain, CUSTOMER_STATUS, ColCustomerSetting


class ColCustomerForm(forms.ModelForm):
    class Meta:
        model = ColCustomer
        exclude = ['disabled']
        widgets = {
            'service_start': forms.DateInput(attrs={'class': 'dateinput'}),
            'service_end': forms.DateInput(attrs={'class': 'dateinput'}),
        }


class ColCustomerDomainForm(forms.ModelForm):
    class Meta:
        model = ColCustomerDomain
        exclude = ['customer', 'disabled']


class ColCustomerSearchForm(forms.Form):
    username = forms.CharField(label=u'用户/公司', required=False)
    customer_id = forms.IntegerField(label=u'用户id', required=False)
    forward_address = forms.CharField(label=u'转发地址', required=False)
    domain = forms.CharField(label=u'域名', required=False)
    mailbox = forms.CharField(label=u'帐号', required=False)
    status = forms.ChoiceField(label=u'状态', required=False, choices=CUSTOMER_STATUS)

class ColCustomerSettingForm(forms.ModelForm):
    class Meta:
        model = ColCustomerSetting
        exclude = ['customer']
