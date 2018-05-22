# coding=utf-8
import re

from django import forms
from models import DomainBlacklist, KeywordBlacklist, MAIL_STATE, CHECK_RESULT, REVIEW_RESULT, CheckSettings, \
    SubjectKeywordBlacklist, BounceSettings, SubjectKeywordWhitelist, FAIL_OR_SUCCESS, \
    SenderBlacklist, InvalidMail, RecipientBlacklist, Settings, CustomKeywordBlacklist, ERROR_TYPE, ValidMailSuffix, \
    AttachmentBlacklist, SenderWhitelist, DSPAM_STUDY, InvalidSenderWhitelist, SpfError, BulkCustomer, SpfChecklist, \
    MAIL_SERVERS, RecipientWhitelist, NoticeSettings, AttachmentTypeBlacklist, CustomerSenderBlacklist, SpamRptSettings, \
    SenderCreditSettings, RelaySenderWhitelist, CreditIntervalSettings, SenderCredit, EdmCheckSettings, \
    CollectRecipientWhitelist, SpamRptBlacklist, CollectRecipientChecklist, SpfIpWhitelist
from apps.core.models import Customer
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField
from ajax_select import make_ajax_field


YES_OR_NO = (
    ('', u'全部'),
    ('True', u'是'),
    ('False', u'否'),
)


class DomainBlacklistForm(forms.ModelForm):
    def clean_domain(self):
        data = self.cleaned_data['domain']
        if DomainBlacklist.objects.exclude(id=self.instance.id).filter(domain=data, disabled=False):
            raise forms.ValidationError(u"重复添加")
        try:
            re.compile(data)
        except:
            raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")

        return data

    class Meta:
        model = DomainBlacklist
        exclude = ['created', 'hits', 'creater', 'operater', 'operate_time']


class KeywordBlacklistForm(forms.ModelForm):
    def clean_keyword(self):

        data = self.cleaned_data['keyword']
        if KeywordBlacklist.objects.exclude(id=self.instance.id).filter(keyword=data, disabled=False):
            raise forms.ValidationError(u"重复添加")
        try:
            re.compile(data)
        except:
            raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")

        return data

    class Meta:
        model = KeywordBlacklist
        exclude = ['created', 'hits', 'creater', 'operater', 'operate_time', 'relay_pass', 'relay_all', 'collect_all',
                   'collect_pass', 'disabled', 'parent']


class KeywordBlacklistBatchForm(forms.ModelForm):
    keyword = forms.CharField(label=u'关键字', widget=forms.Textarea, required=True, help_text=u'一行一条记录, 邮件内容如果含有黑名单关键词'
                                                                                            u'，则将该邮件挂起并交给管理员审核,支持通配符?，例如“发.{1}票”或“发.{2}票”，这样，则“发a票” 或 “发aa票”')

    class Meta:
        model = KeywordBlacklist
        exclude = ['created', 'hits', 'creater', 'operater', 'operate_time', 'relay_pass', 'relay_all', 'collect_all',
                   'collect_pass', 'disabled', 'keyword', 'parent']


class SubjectKeywordBlacklistForm(forms.ModelForm):
    def clean_keyword(self):

        data = self.cleaned_data['keyword']
        if SubjectKeywordBlacklist.objects.exclude(id=self.instance.id).filter(keyword=data, disabled=False):
            raise forms.ValidationError(u"重复添加")
        try:
            re.compile(data)
        except:
            raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")

        return data

    class Meta:
        model = SubjectKeywordBlacklist
        exclude = ['created', 'hits', 'creater', 'operater', 'operate_time', 'relay_pass', 'relay_all', 'collect_all',
                   'collect_pass', 'disabled', 'parent']


class SubjectKeywordBlacklistBatchForm(forms.ModelForm):
    keyword = forms.CharField(label=u'关键字', widget=forms.Textarea, required=True, help_text=u'一行一条记录, 邮件主题如果含有黑名单关键词'
                                                                                            u'，则将该邮件挂起并交给管理员审核,支持通配符?，例如“发.{1}票”或“发.{2}票”，这样，则“发a票” 或 “发aa票”')

    class Meta:
        model = SubjectKeywordBlacklist
        exclude = ['created', 'hits', 'creater', 'operater', 'operate_time', 'relay_pass', 'relay_all', 'collect_all',
                   'collect_pass', 'disabled', 'keyword', 'parent']


class MailBaseSearchForm(forms.Form):
    date_start = forms.DateField(label=u'开始日期', required=False,
                                 widget=forms.DateInput(
                                     attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 12}))
    date = forms.DateField(label=u'结束日期', required=False,
                           widget=forms.DateInput(attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 12}))
    time_start = forms.TimeField(label=u'开始时间', required=False,
                                 widget=forms.DateInput(
                                     attrs={'class': 'dateinput2', 'readonly': 'readonly', 'size': 12}))
    time_end = forms.TimeField(label=u'结束时间', required=False,
                               widget=forms.DateInput(attrs={'class': 'dateinput2', 'readonly': 'readonly', 'size': 10}))
    mail_from = forms.CharField(label=u'发件人', max_length=100, required=False,
                                widget=forms.TextInput(attrs={'size': 12}))
    mail_to = forms.CharField(label=u'收件人', max_length=100, required=False, widget=forms.TextInput(attrs={'size': 12}))
    subject = forms.CharField(label=u'主题', max_length=100, required=False, widget=forms.TextInput(attrs={'size': 12}))
    customers = forms.CharField(label=u'客户', max_length=100, required=False, widget=forms.TextInput(attrs={'size': 12}))
    check = forms.ChoiceField(label=u'检测状态', choices=CHECK_RESULT, required=False)
    show = forms.CharField(label=u'客户', max_length=100, required=False, widget=forms.HiddenInput())
    customer = forms.CharField(label=u'客户', max_length=100, required=False, widget=forms.HiddenInput())
    all_day = forms.CharField(label=u'全部日期', max_length=100, required=False, widget=forms.HiddenInput())
    client_ip = forms.IPAddressField(label=u'客户端IP', max_length=50, required=False,
                                     widget=forms.TextInput(attrs={'size': 12}))
    server_id = forms.ChoiceField(label=u'服务器', choices=MAIL_SERVERS, required=False)
    bulk_sample = forms.BooleanField(label=u'群发样本', required=False)
    is_del_attach = forms.BooleanField(label=u'在线附件', required=False)


class MailSearchForm(MailBaseSearchForm):
    state = forms.ChoiceField(label=u'状态', choices=MAIL_STATE, required=False)
    review = forms.ChoiceField(label=u'审核状态', choices=REVIEW_RESULT, required=False)
    send = forms.ChoiceField(label=u'发送状态', choices=FAIL_OR_SUCCESS, required=False)
    bounce = forms.ChoiceField(label=u'退信状态', choices=FAIL_OR_SUCCESS, required=False)
    error_type = forms.ChoiceField(label=u'错误类型', choices=ERROR_TYPE, required=False)
    dspam_study = forms.ChoiceField(label=u'Dsapm学习', choices=DSPAM_STUDY, required=False)
    return_message = forms.CharField(label=u'发送日志', max_length=100, required=False,
                                     widget=forms.TextInput(attrs={'size': 12}))
    filter_word = forms.CharField(label=u'关键词过滤', max_length=100, required=False,
                                  widget=forms.TextInput(attrs={'size': 12}))
    reviewer = forms.CharField(label=u'审核人', max_length=100, required=False, widget=forms.TextInput(attrs={'size': 12}))


class CheckSettingsForm(forms.ModelForm):
    class Meta:
        model = CheckSettings
        exclude = []


class BounceSettingsForm(forms.ModelForm):
    class Meta:
        model = BounceSettings
        exclude = []


class SubjectKeywordWhitelistForm(forms.ModelForm):
    def clean_keyword(self):

        data = self.cleaned_data['keyword']
        if SubjectKeywordWhitelist.objects.exclude(id=self.instance.id).filter(keyword=data, disabled=False):
            raise forms.ValidationError(u"重复添加")
        try:
            re.compile(data)
        except:
            raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")

        return data

    class Meta:
        model = SubjectKeywordWhitelist
        exclude = ['created', 'hits', 'creater', 'operater', 'operate_time', 'relay', 'direct_reject', 'collect',
                   'c_direct_reject']


class SenderBlacklistForm(forms.ModelForm):
    def clean_keyword(self):
        data = self.cleaned_data['keyword']
        if SenderBlacklist.objects.exclude(id=self.instance.id).filter(keyword=data, disabled=False):
            raise forms.ValidationError(u"重复添加")
        try:
            re.compile(data)
        except:
            raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")

        return data

    class Meta:
        model = SenderBlacklist
        exclude = ['created', 'hits', 'creater', 'operater', 'operate_time', 'disabled', 'parent']


class SenderBlacklistBatchForm(forms.ModelForm):
    keyword = forms.CharField(label=u'关键字', widget=forms.Textarea, required=True, help_text=u'一行一条记录, 发件人如果含有黑名单关键词'
                                                                                            u'，则将该邮件挂起并交给管理员审核,支持通配符?，例如“发.{1}票”或“发.{2}票”，这样，则“发a票” 或 “发aa票”')

    class Meta:
        model = SenderBlacklist
        exclude = ['created', 'hits', 'creater', 'operater', 'operate_time', 'disabled', 'keyword', 'parent']


class InvalidMailForm(forms.ModelForm):
    class Meta:
        model = InvalidMail
        exclude = ['created', 'hits', 'creater', 'operater', 'operate_time']


class RecipientBlacklistForm(forms.ModelForm):
    def clean_keyword(self):
        data = self.cleaned_data['keyword']
        if RecipientBlacklist.objects.exclude(id=self.instance.id).filter(keyword=data, disabled=False):
            raise forms.ValidationError(u"重复添加")
        try:
            re.compile(data)
        except:
            raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")

        return data

    class Meta:
        model = RecipientBlacklist
        exclude = ['created', 'hits', 'creater', 'operater', 'operate_time']


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        exclude = []


class CustomKeywordBlacklistForm(forms.ModelForm):
    def clean_keyword(self):
        data = self.cleaned_data['keyword']
        if CustomKeywordBlacklist.objects.exclude(id=self.instance.id).filter(keyword=data, disabled=False):
            raise forms.ValidationError(u"重复添加")
        # try:
        # re.compile(data)
        # except:
        # raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")
        return data

    class Meta:
        model = CustomKeywordBlacklist
        exclude = ['created', 'hits', 'creater', 'operater', 'operate_time', 'relay', 'direct_reject', 'collect',
                   'c_direct_reject']


class ValidMailSuffixForm(forms.ModelForm):
    def clean_keyword(self):
        data = self.cleaned_data['keyword']
        if ValidMailSuffix.objects.exclude(id=self.instance.id).filter(keyword=data):
            raise forms.ValidationError(u"重复添加")
        return data

    class Meta:
        model = ValidMailSuffix
        exclude = ['created', 'creater', 'operater', 'operate_time']


class DateSearchForm(forms.Form):
    date = forms.DateField(label=u'日期', required=False,
                           widget=forms.DateInput(attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 10}))


class AttachmentBlacklistForm(forms.ModelForm):
    class Meta:
        model = AttachmentBlacklist
        exclude = ['created', 'hits', 'creater', 'operater', 'operate_time', 'disabled', 'parent']


class AttachmentBlacklistBatchForm(forms.ModelForm):
    keyword = forms.CharField(label=u'关键字', widget=forms.Textarea, required=True, help_text=u'一行一条记录, 发件人如果含有黑名单关键词'
                                                                                            u'，则将该邮件挂起并交给管理员审核,支持通配符?，例如“发.{1}票”或“发.{2}票”，这样，则“发a票” 或 “发aa票”')

    class Meta:
        model = AttachmentBlacklist
        exclude = ['created', 'hits', 'creater', 'operater', 'operate_time', 'disabled', 'keyword', 'parent']


class AttachmentTypeBlacklistForm(forms.ModelForm):
    class Meta:
        model = AttachmentTypeBlacklist
        exclude = ['created', 'creater', 'operater', 'operate_time']


class SenderWhitelistForm(forms.ModelForm):
    customer = AutoCompleteSelectField('customer', required=False, help_text=None, label=u'用户/公司',
                                       plugin_options={'autoFocus': True, 'minLength': 1})
    # customer  = make_ajax_field(SenderWhitelist, 'customer', 'customer', help_text=None)

    def __init__(self, *args, **kwargs):
       super(SenderWhitelistForm, self).__init__(*args, **kwargs)  # populates the post
       self.fields['customer'].queryset = Customer.objects.all().order_by('username')
       self.fields['customer'].label_from_instance = lambda obj: "%s ( %s )" % (obj.username, obj.company)

    def clean_customer(self):
        data = self.cleaned_data['customer']
        is_global = self.data.get('is_global', '')
        if is_global:
            return None
        if not is_global and not data:
            raise forms.ValidationError(u"如果是非全局变量，请添加相应客户")
        return data

    def clean_sender(self):
        data = self.cleaned_data['sender'].lower()
        is_domain = self.data.get('is_domain', '')
        customer = self.data.get('customer', '')
        is_global = self.data.get('is_global', '')
        is_regex = self.data.get('is_regex', '')
        if is_global:
            customer = None
        if customer and SenderWhitelist.objects.exclude(id=self.instance.id).filter(sender=data, customer_id=customer):
            raise forms.ValidationError(u"重复添加")

        if not customer and SenderWhitelist.objects.exclude(id=self.instance.id).filter(sender=data,
                                                                                        customer__isnull=True):
            raise forms.ValidationError(u"重复添加")
        """
        if not is_domain and not re.match('^(\w|[-+=.])+@\w+([-.]\w+)*\.(\w+)$', data):
            raise forms.ValidationError(u"邮箱格式添加错误")

        if is_domain and not re.match('^\w+([-.]\w+)*\.(\w+)$', data):
            raise forms.ValidationError(u"域名格式添加错误,　注意前面不要有符号'@'")
        """
        if is_regex:
            try:
                re.compile(data)
            except:
                raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")
        return data

    class Meta:
        model = SenderWhitelist
        exclude = ['creater', 'operater', 'operate_time']


class SenderWhitelistBatchForm(forms.ModelForm):
    customer = AutoCompleteSelectField('customer', required=False, help_text=None, label=u'用户/公司',
                                       plugin_options={'autoFocus': True, 'minLength': 1})
    senders = forms.CharField(label=u'发件人', widget=forms.Textarea, required=True, help_text=u'一行一条记录')

    def __init__(self, *args, **kwargs):
        super(SenderWhitelistBatchForm, self).__init__(*args, **kwargs)  # populates the post
        self.fields['customer'].queryset = Customer.objects.exclude(gateway_status='disabled').order_by('username')
        self.fields['customer'].label_from_instance = lambda obj: "%s ( %s )" % (obj.username, obj.company)

    def clean_customer(self):
        data = self.cleaned_data['customer']
        is_global = self.data.get('is_global', '')
        if not is_global and not data:
            raise forms.ValidationError(u"如果是非全局变量，请添加相应客户")
        return data

    class Meta:
        model = SenderWhitelist
        exclude = ['creater', 'operater', 'operate_time', 'sender']


class SenderWhitelistSearchFrom(forms.Form):
    sender = forms.CharField(label=u'发件人', required=False)
    customer = forms.CharField(label=u'用户/公司', required=False)
    is_global = forms.ChoiceField(label=u'是否全局', required=False, choices=YES_OR_NO)
    is_domain = forms.ChoiceField(label=u'是否域名', required=False, choices=YES_OR_NO)
    disabled = forms.ChoiceField(label=u'是否禁用', required=False, choices=YES_OR_NO)


class CustomerSenderBlacklistForm(forms.ModelForm):
    customer = AutoCompleteSelectField('customer', required=False, help_text=None, label=u'用户/公司',
                                       plugin_options={'autoFocus': True, 'minLength': 1})

    def clean_customer(self):
        data = self.cleaned_data['customer']
        is_global = self.data.get('is_global', False)
        if is_global:
            return None
        if not is_global and not data:
            raise forms.ValidationError(u"如果是非全局变量，请添加相应客户")
        return data

    def clean_sender(self):
        data = self.cleaned_data['sender'].lower()
        is_domain = self.data.get('is_domain', False)
        customer = self.data.get('customer', False)
        is_global = self.data.get('is_global', False)
        is_regex = self.data.get('is_regex', False)
        if is_global:
            customer = None

        if customer and CustomerSenderBlacklist.objects.exclude(id=self.instance.id).filter(sender=data,
                                                                                            customer_id=customer):
            raise forms.ValidationError(u"重复添加")

        if not customer and CustomerSenderBlacklist.objects.exclude(id=self.instance.id).filter(sender=data,
                                                                                                customer__isnull=True):
            raise forms.ValidationError(u'重复添加')

        if is_regex:
            try:
                re.compile(data)
            except:
                raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")
        """
        if not is_domain and not re.match('^(\w|[-+=.])+@\w+([-.]\w+)*\.(\w+)$', data):
            raise forms.ValidationError(u"邮箱格式添加错误")

        if is_domain and not re.match('^\w+([-.]\w+)*\.(\w+)$', data):
            raise forms.ValidationError(u"域名格式添加错误,　注意前面不要有符号'@'")
        """
        return data

    class Meta:
        model = CustomerSenderBlacklist
        exclude = ['creater', 'operater', 'operate_time']


class CustomerSenderBlacklistBatchForm(forms.ModelForm):
    customer = AutoCompleteSelectField('customer', required=False, help_text=None, label=u'用户/公司',
                                       plugin_options={'autoFocus': True, 'minLength': 1})
    senders = forms.CharField(label=u'发件人', widget=forms.Textarea, required=True, help_text=u'一行一条记录')

    def __init__(self, *args, **kwargs):
        super(CustomerSenderBlacklistBatchForm, self).__init__(*args, **kwargs)  # populates the post
        self.fields['customer'].queryset = Customer.objects.all().order_by('username')
        self.fields['customer'].label_from_instance = lambda obj: "%s ( %s )" % (obj.username, obj.company)

    def clean_customer(self):
        data = self.cleaned_data['customer']
        is_global = self.data.get('is_global', False)
        if not is_global and not data:
            raise forms.ValidationError(u"如果是非全局变量，请添加相应客户")
        return data

    class Meta:
        model = CustomerSenderBlacklist
        exclude = ['creater', 'operater', 'operate_time', 'sender']


class CustomerSenderBlacklistSearchForm(forms.Form):
    sender = forms.CharField(label=u'发件人', required=False)
    customer = forms.CharField(label=u'用户/公司', required=False)
    is_global = forms.ChoiceField(label=u'是否全局', required=False, choices=YES_OR_NO)
    is_domain = forms.ChoiceField(label=u'是否域名', required=False, choices=YES_OR_NO)
    disabled = forms.ChoiceField(label=u'是否禁用', required=False, choices=YES_OR_NO)


class InvalidSenderWhitelistForm(forms.ModelForm):
    def clean_sender(self):
        data = self.cleaned_data['sender']
        if InvalidSenderWhitelist.objects.exclude(id=self.instance.id).filter(sender=data):
            raise forms.ValidationError(u"重复添加")
        try:
            re.compile(data)
        except:
            raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")
        return data


    class Meta:
        model = InvalidSenderWhitelist
        exclude = ['creater', 'operater', 'operate_time']


class SpfErrorForm(forms.ModelForm):
    class Meta:
        model = SpfError
        fields = ['note']


class BulkCustomerForm(forms.ModelForm):
    class Meta:
        model = BulkCustomer
        fields = ['note', 'type']


class SpfChecklistForm(forms.ModelForm):
    def clean_domain(self):
        data = self.cleaned_data['domain']
        if SpfChecklist.objects.exclude(id=self.instance.id).filter(domain=data):
            raise forms.ValidationError(u"重复添加")
        return data

    class Meta:
        model = SpfChecklist
        exclude = ['creater', 'operater', 'operate_time']


class RecipientWhitelistForm(forms.ModelForm):
    def clean_keyword(self):
        data = self.cleaned_data['keyword'].lower()
        is_domain = self.data.get('is_domain', '')
        """
        if not is_domain and not re.match("^(\w|[-+=.'])+@\w+([-.]\w+)*\.(\w+)$", data.lower()):
            raise forms.ValidationError(u'收件人白名单邮箱格式添加错误')

        if is_domain and not re.match('^\w+([-.]\w+)*\.(\w+)$', data.lower()):
            raise forms.ValidationError(u"域名格式添加错误,　注意前面不要有符号'@'")
        """

        if RecipientWhitelist.objects.exclude(id=self.instance.id).filter(keyword=data):
            raise forms.ValidationError(u"重复添加")

        # try:
        # re.compile(data)
        #except:
        #    raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")

        return data

    class Meta:
        model = RecipientWhitelist
        exclude = ['created', 'hits', 'creater', 'operater', 'operate_time']


class RecipientWhitelistBatchForm(forms.ModelForm):
    keywords = forms.CharField(label=u'收件人', widget=forms.Textarea, required=True, help_text=u'一行一条记录')

    class Meta:
        model = RecipientWhitelist
        exclude = ['keyword', 'created', 'hits', 'creater', 'operater', 'operate_time']


class NoticeSettingsForm(forms.ModelForm):
    class Meta:
        model = NoticeSettings
        exclude = []


class SenderBlockedRecordSearchForm(forms.Form):
    sender = forms.CharField(label=u'发件人', required=False)
    customer = forms.CharField(label=u'用户/公司', required=False)


class SpamRptSettingsForm(forms.ModelForm):
    class Meta:
        model = SpamRptSettings
        exclude = []

    def clean_html_content(self):
        data = self.cleaned_data['html_content']
        spamrpt_fields = [
            '{id}', '{customer}', '{mail_id}',
            '{check_result}', '{check_message}', '{created}', '{review_result}', '{deliver_time}',
            '{deliver_ip}', '{return_code}', '{return_message}', '{mail_from}', '{sender_name}',
            '{mail_to}', '{subject}', '{client_ip}', '{state}', '{dspam_sig}',
            '{size}', '{error_type}', '{dspam_study}', '{customer_report}', '{server_id}',
            '{reviewer}', '{review_time}', '{attach_name}'
        ]

        if re.search(r'valign="top"', data):
            data = re.sub(r'valign="top"', 'nowrap="nowrap"', data)

        fields_list = re.findall(r'(\{.*?\})', data)
        for key in fields_list:
            if key not in spamrpt_fields:
                tmp_list = re.findall(r'(\{.*?\<)', key)
                if tmp_list:
                    m = tmp_list[0].replace('<', '')
                    msg = u"“%s” 表单字段信息不存在，请严格按照备注栏添加字段信息，如{mail_from}表示发件人。" % m
                    raise forms.ValidationError(msg)
                tmp_list = re.findall(r'(\<td nowrap="nowrap"\>.*?\})', key)
                if tmp_list:
                    m = tmp_list[0].replace('<td nowrap="nowrap">', '')
                    msg = u"“%s” 表单字段信息不存在，请严格按照备注栏添加字段信息，如{mail_from}表示发件人。" % m
                    raise forms.ValidationError(msg)
                msg = u"“%s” 表单字段信息不存在，请严格按照备注栏添加字段信息，如{mail_from}表示发件人。" % key
                raise forms.ValidationError(msg)

        tmp_list = re.findall(r'(\<td nowrap="nowrap"\>).*?(\{.*?\<)', data)
        for flag, pair in tmp_list:
            tmp_list = re.findall(r'(\{.*?\})', pair)
            if not tmp_list:
                tmp_list = re.findall(r'(\{.*?\<)', pair)
                if tmp_list:
                    m = tmp_list[0].replace('<', '')
                    msg = u"“%s” 表单字段信息不存在，请严格按照备注栏添加字段信息，如{mail_from}表示发件人。" % m
                    raise forms.ValidationError(msg)

        tmp_list = re.findall(r'(\<td nowrap="nowrap"\>.*?\})', data)
        for pair in tmp_list:
            tmp_list = re.findall(r'(\{.*?\})', pair)
            if not tmp_list:
                tmp_list = re.findall(r'(\>.*?\})', pair)
                if tmp_list:
                    m = tmp_list[0].replace('>', '')
                    msg = u"“%s” 表单字段信息不存在，请严格按照备注栏添加字段信息，如{mail_from}表示发件人。" % m
                    raise forms.ValidationError(msg)

        if re.search(r'valign="top"', data):
            data = re.sub(r'valign="top"', ' nowrap="nowrap" ', data)
        data = data.replace('<br />', '')

        return data


class SenderCreditSettingsForm(forms.ModelForm):
    class Meta:
        model = SenderCreditSettings
        exclude = []


class SenderCreditForm(forms.ModelForm):
    class Meta:
        model = SenderCredit
        exclude = ['sender', 'update_time']


class SenderCreditBaseSearchForm(forms.Form):
    sender = forms.CharField(label=u'发件人', required=False)


class RelaySenderWhitelistSearchForm(forms.Form):
    sender = forms.CharField(label=u'发件人', required=False)


class RelaySenderWhitelistForm(forms.ModelForm):
    customer = AutoCompleteSelectField('customer', required=False, help_text=None, label=u'用户/公司',
                                       plugin_options={'autoFocus': True, 'minLength': 1})

    def clean_sender(self):
        data = self.cleaned_data['sender'].lower()
        """
        if not re.match("^(\w|[-+='.])+@\w+([-.]\w+)*\.(\w+)$", data.lower()):
            raise forms.ValidationError(u'收件人白名单邮箱格式添加错误')
        """
        if RelaySenderWhitelist.objects.exclude(id=self.instance.id).filter(sender=data):
            raise forms.ValidationError(u"重复添加")
        return data

    class Meta:
        model = RelaySenderWhitelist
        exclude = ['created', 'creater', 'operater', 'operate_time']


class RelaySenderWhitelistBatchForm(forms.ModelForm):
    customer = AutoCompleteSelectField('customer', required=False, help_text=None, label=u'用户/公司',
                                       plugin_options={'autoFocus': True, 'minLength': 1})
    senders = forms.CharField(label=u'发件人', widget=forms.Textarea, required=True, help_text=u'一行一条记录')

    class Meta:
        model = RelaySenderWhitelist
        exclude = ['sender', 'created', 'creater', 'operater', 'operate_time']


class CreditIntervalSettingsForm(forms.ModelForm):
    def check_credit(self, seq=None):
        seq = seq if isinstance(seq, list) else []
        seqlen = len(seq)
        if seqlen == 1:
            seq[0]['credit_e'] = float('inf') if not seq[0]['credit_e'] else seq[0]['credit_e']
            if seq[0]['credit_b'] == seq[0]['credit_e']:
                raise forms.ValidationError(u'区间起和区间止不能设置为相同值！')
        if seqlen >= 2:
            for i in range(seqlen):
                seq[i]['credit_e'] = float('inf') if not seq[i]['credit_e'] else seq[i]['credit_e']
                if seq[i]['credit_b'] == seq[i]['credit_e']:
                    raise forms.ValidationError(u'区间起和区间止不能设置为相同值！')
                for j in range(i + 1, seqlen):
                    seq[j]['credit_e'] = float('inf') if not seq[i]['credit_e'] else seq[j]['credit_e']
                    if seq[j]['credit_b'] < seq[i]['credit_e'] <= seq[j]['credit_e'] or \
                                            seq[j]['credit_b'] <= seq[i]['credit_b'] < seq[j]['credit_e'] or \
                                            seq[i]['credit_b'] < seq[j]['credit_e'] <= seq[i]['credit_e'] or \
                                            seq[i]['credit_b'] <= seq[j]['credit_b'] < seq[i]['credit_e']:
                        raise forms.ValidationError(u'区间设置有重叠，请核实信誉度区间！')
        return True

    def clean(self):
        credit_b = self.cleaned_data.get('credit_b')
        credit_e = self.cleaned_data.get('credit_e')
        if credit_b > credit_e:
            raise forms.ValidationError(u'区间起不能大于区间止！')
        credit_interval = CreditIntervalSettings.objects.exclude(id=self.instance.id).values_list('credit_b',
                                                                                                  'credit_e')
        credit_interval = list(credit_interval)
        credit_interval.insert(0, (credit_b, credit_e))
        vals = [dict(zip(('credit_b', 'credit_e'), each)) for each in credit_interval]
        self.check_credit(vals)
        return self.cleaned_data

    class Meta:
        model = CreditIntervalSettings
        exclude = []


class EdmCheckSettingsForm(forms.ModelForm):
    class Meta:
        model = EdmCheckSettings
        exclude = []


class CollectRecipientWhitelistForm(forms.ModelForm):

    customer = AutoCompleteSelectField('customer', required=False, help_text=None, label=u'用户/公司',
                                       plugin_options={'autoFocus': True, 'minLength': 1})

    class Meta:
        model = CollectRecipientWhitelist
        exclude = ['created', 'creater', 'operater', 'operate_time']


class CollectRecipientWhitelistBatchForm(forms.ModelForm):
    keywords = forms.CharField(label=u'收件人', widget=forms.Textarea, required=True, help_text=u'一行一条记录')

    class Meta:
        model = CollectRecipientWhitelist
        exclude = ['keyword', 'created', 'creater', 'operater', 'operate_time']

class CollectRecipientChecklistForm(forms.ModelForm):

    def clean_keyword(self):
        data = self.cleaned_data['keyword'].lower()
        if CollectRecipientChecklist.objects.exclude(id=self.instance.id).filter(keyword=data, disabled=False):
            raise forms.ValidationError(u"重复添加")
        try:
            re.compile(data)
        except:
            raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")
        return data

    class Meta:
        model = CollectRecipientChecklist
        exclude = ['created', 'creater', 'operater', 'operate_time']

class ActiveSenderForm(forms.Form):
    date = forms.CharField(label=u'日期', required=False,
                           widget=forms.DateInput(attrs={'class': 'dateinput ', 'readonly': 'readonly', 'size': 20}))
    customer_id = forms.CharField(label=u'客户ID', max_length=100, required=False, widget=forms.TextInput(attrs={'size': 12}))

class SpamRptBlacklistForm(forms.ModelForm):
    customer = AutoCompleteSelectField('customer', required=True, help_text=None, label=u'用户/公司',
                                       plugin_options={'autoFocus': True, 'minLength': 1})


    def clean_recipient(self):
        data = self.cleaned_data['recipient'].lower()
        if SpamRptBlacklist.objects.exclude(id=self.instance.id).filter(recipient=data):
            raise forms.ValidationError(u"重复添加")
        return data

    def clean_customer(self):
        data = self.cleaned_data['customer']
        return data

    class Meta:
        model = SpamRptBlacklist
        exclude = ['created', 'creater', 'operater', 'operate_time']


class SpamRptBlacklistBatchForm(forms.ModelForm):
    customer = AutoCompleteSelectField('customer', required=True, help_text=None, label=u'用户/公司',
                                       plugin_options={'autoFocus': True, 'minLength': 1})
    recipients = forms.CharField(label=u'收件人', widget=forms.Textarea, required=True, help_text=u'一行一条记录')

    def __init__(self, *args, **kwargs):
        super(SpamRptBlacklistBatchForm, self).__init__(*args, **kwargs)  # populates the post
        self.fields['customer'].queryset = Customer.objects.all().order_by('username')
        self.fields['customer'].label_from_instance = lambda obj: "%s ( %s )" % (obj.username, obj.company)

    class Meta:
        model = SpamRptBlacklist
        exclude = ['created', 'creater', 'operater', 'operate_time', 'recipient']


class SpfIpWhitelistForm(forms.ModelForm):

    def clean_keyword(self):
        data = self.cleaned_data['keyword'].strip()
        if not re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", data):
            raise forms.ValidationError(u"ip格式不正确")
        return data

    class Meta:
        model = SpfIpWhitelist
        exclude = ['created', 'creater', 'operater', 'operate_time']

