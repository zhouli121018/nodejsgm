# -*- coding:utf-8 -*-
import json
import time
import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import CoreGroup, CoreGroupMember
from .models import PASSWD_OHER, CHEACK_ATTACH_SIZE, MATCH_BLACK, CHECK_SPAM, CHECK_OBJECT, CHECK_LOCAL, CHECK_OUTSIDE
from app.utils.regex import pure_email_regex
from app.core.models import Mailbox

PASSWD_OTHER_LETTER = (
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
    ('13', '13'),
    ('14', '14'),
    ('15', '15'),
    ('16', '16'),
)

class CoreGroupForms(forms.ModelForm):
    domain_id = forms.IntegerField(label=_(u'域名'), required=False, widget=forms.HiddenInput())
    passwd_other_bak = forms.MultipleChoiceField(label=_(u'其他密码规则设置'), required=False, choices=PASSWD_OHER)
    passwd_other_letter = forms.ChoiceField(required=True, choices=PASSWD_OTHER_LETTER, initial='8')

    check_attach_bak = forms.MultipleChoiceField(label=_(u'检查附件'), required=False, choices=CHEACK_ATTACH_SIZE)
    match_black_bak = forms.MultipleChoiceField(label=_(u'匹配黑名单'), required=False, choices=MATCH_BLACK)
    check_spam_bak = forms.MultipleChoiceField(label=_(u'反垃圾引擎'), required=False, choices=CHECK_SPAM)
    check_object_bak = forms.MultipleChoiceField(label=_(u'检测对象'), required=False, choices=CHECK_OBJECT)
    check_local_bak = forms.MultipleChoiceField(label=_(u'本域进站邮件'), required=False, help_text=_(u"“反垃圾功能”和“反病毒功能”开启后，这里对应的勾选框才会生效"), choices=CHECK_LOCAL)
    check_outside_bak = forms.MultipleChoiceField(label=_(u'外域进站邮件'), required=False, help_text=_(u"“反垃圾功能”和“反病毒功能”开启后，这里对应的勾选框才会生效"), choices=CHECK_OUTSIDE)

    def __init__(self, domain_id, domain, *args, **kwargs):
        super(CoreGroupForms, self).__init__(*args, **kwargs)
        self.domain_id=domain_id
        self.domain=domain
        if self.instance.pk:
            groupobj = self.instance
            self.passwd_other = groupobj.check_spam and json.loads(groupobj.passwd_other) or {}
            self.passwd_size2 = self.passwd_other['passwd_size2'] if 'passwd_size2' in self.passwd_other else '8'
            self.check_attach = groupobj.check_attach and json.loads(groupobj.check_attach) or {}
            self.match_black = groupobj.match_black and json.loads(groupobj.match_black) or {}
            self.check_spam = groupobj.check_spam and json.loads(groupobj.check_spam) or {}
            self.check_object = groupobj.check_object and json.loads(groupobj.check_object) or {}
            self.check_local = groupobj.check_local and json.loads(groupobj.check_local) or {}
            self.check_outside = groupobj.check_outside and json.loads(groupobj.check_outside) or {}
        else:
            self.passwd_other = {u'passwd_size2': u'8', u'passwd_size': u'passwd_size', u'passwd_digital': u'passwd_digital', u'passwd_name': u'passwd_name'}
            self.passwd_size2 = self.passwd_other['passwd_size2'] if 'passwd_size' in self.passwd_other else '8'
            self.check_attach = {u'low': u'low', u'high': u'high'}
            self.match_black = {u'sender': u'sender', u'subject': u'subject', u'content': u'content', u'attach': u'attach'}
            self.check_spam = {u'dspam': u'dspam', u'spamassassion': u'spamassassion'}
            self.check_object = {u'local': u'local', u'outside': u'outside'}
            self.check_local = {u'spam': u'spam', u'virus': u'virus'}
            self.check_outside = {u'spam': u'spam', u'virus': u'virus'}

        self.fields['passwd_start'].widget.attrs.update({'readonly': 'readonly'})
        self.fields['spam_subject_flag'].widget.attrs.update({'placeholder': '[ ** * SPAM ** *]'})
        self.fields['send_isolate_name'].widget.attrs.update({'placeholder': 'spamreporter'})
        self.fields['isolate_url'].widget.attrs.update({'placeholder': 'http://mail.test.com'})
        self.fields['mail_space'].widget.attrs.update({ 'addon': u'MB'})
        self.fields['net_space'].widget.attrs.update({'addon': u'MB'})
        self.fields['allow_out_size'].widget.attrs.update({'addon': u'MB'})
        self.fields['passwd_day'].widget.attrs.update({'addon': _(u'天')})
        self.fields['isolate_day'].widget.attrs.update({'addon': _(u'天')})

    class Meta:
        model = CoreGroup
        exclude = ['passwd_other', 'check_attach', 'match_black', 'check_spam', 'check_object', 'check_local', 'check_outside']

    def clean_domain_id(self):
        return self.domain_id

    def clean_passwd_start(self):
        passwd_start = self.cleaned_data.get('passwd_start')
        if isinstance(passwd_start, datetime.datetime):
            t_tuple = passwd_start.timetuple()
            expire = int(time.mktime(t_tuple))
            now = time.time()
            if expire > now:
                passwd_start = datetime.datetime.now()
        else:
            passwd_start = None
        return passwd_start

    def clean_name(self):
        name = self.cleaned_data.get('name')
        name = name.strip()
        if not name:
            raise forms.ValidationError(_(u"请填写组名称。",))
        if CoreGroup.objects.exclude(id=self.instance.id).filter(
                domain_id=self.domain_id, name=name).exists():
            raise forms.ValidationError(_(u"组名称存在。", ))
        return name

    def __get_bak(self, field):
        value = self.cleaned_data.get(field)
        return dict(zip(value, value))

    def clean(self):
        passwd_other_bak = self.cleaned_data.get('passwd_other_bak')
        passwd_other = dict(zip(passwd_other_bak, passwd_other_bak))
        if 'passwd_size' in passwd_other_bak:
            passwd_other_letter = self.cleaned_data.get('passwd_other_letter')
            passwd_other.update(passwd_size2=passwd_other_letter)
        self.passwd_other = passwd_other

        self.check_attach = self.__get_bak('check_attach_bak')
        self.match_black = self.__get_bak('match_black_bak')
        self.check_spam = self.__get_bak('check_spam_bak')
        self.check_object = self.__get_bak('check_object_bak')
        self.check_local = self.__get_bak('check_local_bak')
        self.check_outside = self.__get_bak('check_outside_bak')
        return self.cleaned_data

    def save(self, commit=True):
        o = super(CoreGroupForms, self).save(commit=False)
        o.passwd_other = json.dumps(self.passwd_other)
        o.check_attach = json.dumps(self.check_attach)
        o.match_black = json.dumps(self.match_black)
        o.check_spam = json.dumps(self.check_spam)
        o.check_object = json.dumps(self.check_object)
        o.check_local = json.dumps(self.check_local)
        o.check_outside = json.dumps(self.check_outside)

        if commit:
            o.save()
        return o

class CoreGroupMemberForm(forms.ModelForm):
    group = forms.CharField(label=_(u'组'), required=False, widget=forms.HiddenInput())

    def __init__(self, group_obj, *args, **kwargs):
        super(CoreGroupMemberForm, self).__init__(*args, **kwargs)
        self.group=group_obj

    class Meta:
        model = CoreGroupMember
        fields = ['group', 'address']

    def clean_group(self):
        return self.group

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address:
            raise forms.ValidationError(_(u"请输入邮箱。", ))
        if not pure_email_regex(address):
            raise forms.ValidationError(_(u"输入的邮箱不合法。", ))
        if not Mailbox.objects.filter(mailbox=address).exists():
            raise forms.ValidationError(_(u"邮件地址不在邮件账号中。", ))
        if CoreGroupMember.objects.exclude(id=self.instance.id).filter(
                group=self.group, address=address).exists():
            raise forms.ValidationError(_(u"组成员已存在列表中。", ))
        return address

    def save(self, commit=True):
        o = super(CoreGroupMemberForm, self).save(commit=False)
        o.set_name()
        if commit:
            o.save()
        return o