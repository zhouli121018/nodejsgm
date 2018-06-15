# coding=utf-8
from django import forms

from app.core.models import Customer, CustomerDomain


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['linkman', 'phone', 'mobile', 'email', 'im', 'address']


class CustomerDomainForm(forms.ModelForm):
    class Meta:
        model = CustomerDomain
        fields = ['domain']
