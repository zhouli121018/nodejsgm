#coding=utf-8
from django import forms
from app.address.models import MailList, RecipientBlacklist

from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from lib.validators import check_email_ordomain

class MailListForm(forms.ModelForm):
    customer = forms.CharField(label=_(u'客户'), required=False, widget=forms.HiddenInput())

    def __init__(self, customer, *args, **kwargs):
        super(MailListForm, self).__init__(*args, **kwargs)
        self.customer = customer

    def clean_customer(self):
        return self.customer

    def clean_subject(self):
        data = self.cleaned_data['subject']

        if not data:
            raise forms.ValidationError(_(u"请填写联系人分类名称"))
        return data

    class Meta:
        model = MailList
        fields =['customer', 'subject', 'description']
        # exclude = ['id', 'created', 'updated', 'isvalid', 'count_all', 'count_err', 'count_real', 'count_subscriber', 'last_in_status', 'is_allow_export', 'is_smtp', 'is_upset_flag', 'status', 'manager']


class RecipientBlacklistForm(forms.ModelForm):
    user = forms.CharField(label=_(u'客户'), required=False, widget=forms.HiddenInput())

    def __init__(self, user, *args, **kwargs):
        super(RecipientBlacklistForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_user(self):
        return self.user

    def clean_addr(self):
        data = self.cleaned_data['addr']
        data = data and data.strip() or ""
        if not data:
            raise forms.ValidationError(_(u"请填写黑名单"))
        if not check_email_ordomain(data):
            raise forms.ValidationError(_(u"请输入正确的地址格式"))
        if RecipientBlacklist.objects.exclude(id=self.instance.id).filter(user=self.user, addr=data).exists():
            raise forms.ValidationError(_(u"重复添加"))
        return data

    class Meta:
        model = RecipientBlacklist
        fields =['user', 'addr']


class RecipientBlacklistBatchForm(forms.ModelForm):
    addrs = forms.CharField(label=u'黑名单地址', widget=forms.Textarea, required=True,
                            help_text=u'一行一条记录, 当对象为邮箱时请在“地址”里填写邮件地址，对象为域时请在“地址”中填写“@域名”，eg:“@test.com”')
    class Meta:
        model = RecipientBlacklist
        fields =['addrs']


from captcha.fields import CaptchaField
class CaptchaTestForm(forms.Form):
    captcha = CaptchaField()

