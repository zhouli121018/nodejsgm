# coding=utf-8
from django import forms
from app.task.models import SendTask
from app.template.models import SendTemplate
from app.address.models import MailList
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache

class SendTaskForm(forms.ModelForm):
    user = forms.CharField(label=u'客户', required=False, widget=forms.HiddenInput())
    # send_name = forms.CharField(label=u'发送批次', widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    # template = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label=u"选择邮件模板")
    # maillist = forms.ChoiceField(label=u'选择联系人列表')
    # sender = forms.ChoiceField(label=u'发件人')

    def __init__(self, user, *args, **kwargs):
        super(SendTaskForm, self).__init__(*args, **kwargs)
        self.user = user
        # self.fields['template'].choices = [(x.id, x) for x in SendTemplate.objects.filter(user=user, name__isnull=False)]
        # self.fields['maillist'].choices = [(x.id, x) for x in MailList.objects.filter(customer=user)]

    def clean_user(self):
        return self.user

    class Meta:
        model = SendTask
        exclude = []
        # fields = ['user']
        # exclude = [
        #     'id', 'send_acct_type', 'send_acct_domain', 'send_replyto', 'send_fullname',
        #     'send_maillist', 'send_maillist_id',
        #     'send_qty', 'send_qty_remark', 'send_time',
        #     'send_status', 'verify_status', 'time_start', 'time_end', 'updated', 'status'
        # ]


class SendTaskSearchForm(forms.Form):
    name = forms.CharField(label=u'任务名称', required=False)


class TaskExportForm(forms.Form):
    export_open_or_click = forms.ChoiceField(label=_(u"导出类型"), choices=( ('open', _(u"打开")), ('click', _(u"点击")) ), initial="open")
    export_is_new_maillist = forms.BooleanField(label=_(u'是否导入到新分类'), widget=forms.CheckboxInput(attrs={
        "autocomplete": "off",
        "onchange": "onchangeIsNewMaillist();",
    }))
    export_maillist_name = forms.CharField(label=_(u'分类名称'), initial=_(u"打开/点击地址"), max_length=50,
                                           help_text=_(u"默认名称为：打开/点击地址，打开/点击地址将导入此分类中"))
    export_maillist_id = forms.ModelChoiceField(
        label=_(u'选择地址池'),
        queryset=None,
        widget=forms.Select(attrs={
            #"data-placeholder": _(u"请选择地址池"),
            "autocomplete": "off",
            "class": "select2 ",
        }), help_text=_(u"选择一个地址分类，打开/点击地址将导入此分类中"))

    def __init__(self, user, *args, **kwargs):
        super(TaskExportForm, self).__init__(*args, **kwargs)
        lists = MailList.objects.filter(
            customer=user).filter(
            isvalid=True, is_smtp=False).order_by('-id')[:500]
        self.fields['export_maillist_id'].queryset= lists

