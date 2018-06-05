# -*- coding:utf-8 -*-
import time
from django import forms
from .models import ExtList, ExtListMember
from django.utils.translation import ugettext_lazy as _
from app.core.models import Mailbox
from app.utils.regex import pure_email_regex

class ExtListForm(forms.ModelForm):
    domain_id = forms.IntegerField(label=_(u'域名'), required=False, widget=forms.HiddenInput())

    def __init__(self, domain_id, domain, listname, address, is_import, *args, **kwargs):
        super(ExtListForm, self).__init__(*args, **kwargs)
        self.domain_id=domain_id
        self.domain=domain
        self.listname=listname
        self.address=address
        self.is_import=is_import
        self.fields['description'].widget.attrs.update({'rows': '3'})
        if self.instance.pk:
            self.fields['address'].widget.attrs.update({'readonly': 'readonly'})
            if self.instance.is_everyone:
                self.fields['listname'].widget.attrs.update({'readonly': 'readonly'})
        else:
            self.fields['address'].widget.attrs.update({'addon': '@{}'.format(self.domain)})

    def clean_domain_id(self):
        return self.domain_id

    def clean_listname(self):
        # if self.listname:
        #     return self.listname
        listname = self.cleaned_data.get('listname')
        listname = listname and listname.strip() or None
        if not listname:
            raise forms.ValidationError(_(u"请填写邮件邮件列表名称。",))
        return listname

    def clean_address(self):
        if self.address:
            return self.address
        address = self.cleaned_data.get('address')
        address = address and address.strip() or None
        if not address:
            raise forms.ValidationError(_(u"请填写邮件列表地址。", ))
        if not self.is_import:
            address = u"{}@{}".format(address, self.domain)
        if not pure_email_regex(address):
            raise forms.ValidationError(_(u"输入的邮件列表地址不合法。", ))
        if ExtList.objects.exclude(id=self.instance.id).filter(
                address=address, domain_id=self.domain_id).exists():
            raise forms.ValidationError(_(u"邮件列表地址已存在列表中。", ))
        return address

    class Meta:
        model = ExtList
        fields = ('domain_id', 'listname', 'address', 'description', 'permission', 'disabled')


class ExtListMemberForm(forms.ModelForm):
    list_id = forms.IntegerField(label=_(u'列表'), required=False, widget=forms.HiddenInput())
    update_time = forms.IntegerField(label=_(u'更新时间'), required=False, widget=forms.HiddenInput())

    def __init__(self, list_id, listobj, *args, **kwargs):
        super(ExtListMemberForm, self).__init__(*args, **kwargs)
        self.list_id = list_id
        self.listobj = listobj
        if self.instance.pk:
            self.fields['address'].widget.attrs.update({'readonly': 'readonly'})
            self.fields['name'].widget.attrs.update({'readonly': 'readonly'})
        if self.listobj.is_everyone:
            self.fields['name'].widget.attrs.update({'readonly': 'readonly', 'type': 'hidden'})
            self.fields['permit'].widget.attrs.update({'readonly': 'readonly'})
            self.fields['permit'].initial = '1'

    def clean_list_id(self):
        return self.list_id

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address:
            raise forms.ValidationError(_(u"请填写邮件地址。",))
        if not pure_email_regex(address):
            address = u'{}@{}'.format(address, self.listobj.domain)
            if not pure_email_regex(address):
                raise forms.ValidationError(_(u"输入的邮件地址不合法。", ))
        if ExtListMember.objects.exclude(id=self.instance.id).filter(
                address=address, list_id=self.list_id).exists():
            raise forms.ValidationError(_(u"邮件地址已存在列表中。", ))
        if self.listobj.is_everyone:
            if not Mailbox.objects.filter(mailbox=address).exists():
                raise forms.ValidationError(_(u"邮件地址不在邮件账号中。", ))
        return address

    def clean_name(self):
        address = self.cleaned_data.get('address')
        if self.listobj:
            obj = Mailbox.objects.filter(mailbox=address).first()
            return obj and obj.name or None
        return address

    def clean_update_time(self):
        return int(time.time())

    def save(self, commit=True):
        mem = super(ExtListMemberForm, self).save(commit=False)
        if not mem.name:
            mem.name = ( "@".join(mem.address.split('@')[:-1]) ).upper()
        if self.listobj.is_everyone:
            mem.permit = '1'
        mem.set_domain_id(self.list_id)
        if commit:
            mem.save()
        return mem

    class Meta:
        model = ExtListMember
        fields = ('address', 'name', 'permit', 'update_time', 'list_id',)

class ExcelTxtImport(forms.Form):
    txtfile = forms.FileField(label=u'文件导入', required=True)

    def __init__(self, *args, **kwargs):
        super(ExcelTxtImport, self).__init__(*args, **kwargs)
        self.file_name = None
        self.file_ext = None
        self.file_obj = None

    def clean_txtfile(self):
        f = self.files.get('txtfile', None)
        if not f:
            raise forms.ValidationError(_(u"请选择文件。", ))
        file_name = f.name
        fext = file_name.split('.')[-1]
        if fext not in ('xls', 'xlxs', 'csv', 'txt'):
            raise forms.ValidationError(_(u"只支持excel、txt、csv文件导入。", ))
        self.file_name = file_name
        self.file_ext = fext
        self.file_obj = f
        return f

