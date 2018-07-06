# coding=utf-8
import re
from django import forms
from app.core.configs import ACTION_TYPE


class CoreLogSearchForm(forms.Form):
    action = forms.ChoiceField(label=u'操作类型', choices=ACTION_TYPE, required=False)
    date_start = forms.DateField(label=u'开始日期', required=False,
                           widget=forms.DateInput(attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 12}))
    date_end = forms.DateField(label=u'结束日期', required=False,
                           widget=forms.DateInput(attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 12}))