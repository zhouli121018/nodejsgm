# coding=utf-8
from django import forms
from models import NotExistFlag, BigQuotaFlag, SpamFlag, NotRetryFlag, SpfFlag, HighRiskFlag, GreyListFlag


class NotExistFlagForm(forms.ModelForm):
    class Meta:
        model = NotExistFlag
        exclude = ['creater', 'operater', 'operate_time']


class BigQuotaFlagForm(forms.ModelForm):
    class Meta:
        model = BigQuotaFlag
        exclude = ['creater', 'operater', 'operate_time']


class SpamFlagForm(forms.ModelForm):
    class Meta:
        model = SpamFlag
        exclude = ['creater', 'operater', 'operate_time']


class NotRetryFlagForm(forms.ModelForm):
    class Meta:
        model = NotRetryFlag
        exclude = ['creater', 'operater', 'operate_time']

class SpfFlagForm(forms.ModelForm):
    class Meta:
        model = SpfFlag
        exclude = ['creater', 'operater', 'operate_time']

class HighRiskFlagForm(forms.ModelForm):
    class Meta:
        model = HighRiskFlag
        exclude = ['creater', 'operater', 'operate_time']

class GreyListFlagForm(forms.ModelForm):
    class Meta:
        model = GreyListFlag
        exclude = ['creater', 'operater', 'operate_time']
