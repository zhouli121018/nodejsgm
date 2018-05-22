# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from app.template.models import SendTemplate, SendSubject, RefTemplateCategory

class SendTemplateForm(forms.ModelForm):

    user = forms.CharField(label=_(u'客户'), required=False, widget=forms.HiddenInput())
    subject = forms.CharField(label=_(u"主题"), required=False, widget=forms.HiddenInput())
    text_content = forms.CharField(label=_(u'文本'), required=False, widget=forms.HiddenInput())
    name = forms.CharField(label=_(u"模板名称"), required=True, max_length=100)
    content = forms.CharField(label=_(u"内容"), required=True, widget=forms.Textarea)
    issync = forms.BooleanField(label=_(u"同步"), required=False, initial=True, widget=forms.HiddenInput)
    size = forms.IntegerField(label=_(u"大小"), required=False, initial=0, widget=forms.HiddenInput)
    result = forms.CharField(label=_(u"结果"), required=False, widget=forms.HiddenInput)
    content_type = forms.IntegerField(label=_(u"类型"), required=False, initial=1, widget=forms.HiddenInput)

    class Meta:
        model = SendTemplate
        fields = [
            "user", "name", "content", "text_content", "subject",
            "encoding", "character", "image_encode", "attachtype",
            "size", "issync", "result", "content_type"
        ]

    def __init__(self, user, template_id, subject_list=None, *args, **kwargs):
        super(SendTemplateForm, self).__init__(*args, **kwargs)
        self.user = user
        self.issync = True
        self.result = ""
        self.content_type = 1
        self.size = 0
        self.add_or_modify = True if self.instance.content else False
        lists = SendSubject.objects.filter(template_id=template_id).values_list("id", "subject")
        if not lists:
            lists = [("1", "")]
        self.subjectlists = lists
        self.subject_list=subject_list

    def clean_user(self):
        return self.user

    def clean_issync(self):
        return True

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content:
            raise forms.ValidationError(_(u"请填写邮件内容！"))
        return content

    def clean_result(self):
        return ""

    def clean_content_type(self):
        return 1

    def clean_size(self):
        content = self.cleaned_data.get('content')
        return content and len(content) or 0

    def clean_text_content(self):
        return u'''如果邮件内容无法正常显示请以超文本格式显示HTML邮件！\n
        （If the content of the message does not display properly, please display the HTML message in hypertext format!）'''

    def clean_subject(self):
        T = True
        lists = []
        subject = self.cleaned_data.get('subject')
        for index, value in enumerate(self.subject_list):
            value = value.strip()
            if value:
                T = False
                subject = value
            lists.append( (index, value) )
        self.subjectlists = lists
        if T:
            raise forms.ValidationError(_(u"请至少填写一个邮件主题！"))
        return subject

    def saveSubject(self, obj):
        SendSubject.objects.filter(template=obj).delete()
        bulk = []
        for value in self.subject_list:
            value = value.strip()
            if value:
                bulk.append( SendSubject(template=obj, subject=value) )
        if bulk:
            SendSubject.objects.bulk_create(bulk)
        return






