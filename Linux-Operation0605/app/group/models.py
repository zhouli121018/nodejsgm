# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from app.core.models import Domain, Mailbox

SEND_LIMIT = (
    (1, _(u'不限制邮件发送')),
    (2, _(u'禁止发送所有邮件')),
    (3, _(u'只发送本地域邮件')),
    (4, _(u'可发送指定外域邮件')),
    (5, _(u'可发送本地所有域邮件')),
)
RECV_LIMIT = (
    (1, _(u'不限制邮件接收')),
    (2, _(u'禁此接收所有邮件')),
    (3, _(u'只接收本地域邮件')),
    (4, _(u'可接收指定外域邮件')),
)
PASSWD_TYPE = (
    (2, _(u'必须包含两种字符')),
    (3, _(u'必须包含三种字符')),
    (4, _(u'必须包含四种字符')),
)
PASSWD_OHER = (
    ('passwd_size', _(u'密码长度为 8 至16位')),
    ('passwd_name', _(u'密码不能包含账号')),
    ('passwd_digital', _(u'连续3位及以上数字不能连号（例如：123、654）')),
    ('passwd_letter', _(u'连续3位及以上字母不能连号（例如：abc、cba）')),
    ('passwd_letter2', _(u'密码不能包含连续3个及以上相同字符（例如：aaa、rrr）')),
    ('passwd_name2', _(u'密码不能包含用户姓名大小写全拼')),
)
CHEACK_ATTACH_SIZE = (
    ('low', _(u'小危附件')),
    ('high', _(u'高危附件')),
)
MATCH_BLACK = (
    ('sender', _(u'发件人黑名单')),
    ('subject', _(u'主题黑名单')),
    ('content', _(u'内容黑名单')),
    ('attach', _(u'附件黑名单')),
)

CHECK_SPAM = (
    ("dspam", "Dspam"),
    ("spamassassion", " Spamassassion"),
)
SPAM_FOLDER = (
    ("spam", _(u"垃圾箱")),
    ("sequester", _(u"隔离队列")),
    ("inbox", _(u"收件箱")),
)
CHECK_OBJECT = (
    ("local", _(u"本域进站邮件")),
    ("outside", _(u"外域进站邮件")),
)
CHECK_LOCAL = (
    ("spam", _(u"开启反垃圾")),
    ("virus", _(u"开启反病毒")),
)
CHECK_OUTSIDE = (
    ("spam", _(u"开启反垃圾")),
    ("virus", _(u"开启反病毒")),
)

PASSWD_LEVEL = (
    (1, _(u"秘密")),
    (2, _(u"机密")),
    (3, _(u"绝密")),
)

class CoreGroup(models.Model):
    domain_id = models.IntegerField(u'所属域名ID', default=0)
    name = models.CharField(_(u'组名称'), max_length=100, blank=False, null=False)
    description = models.TextField(_(u'组描述'), null=True, blank=True)

    # 常规设置
    mail_space = models.IntegerField(_(u'邮箱空间'), default=0)
    net_space = models.IntegerField(_(u"网络硬盘空间"), default=0)
    allow_out_size = models.IntegerField(_(u"允许外发附件大小"), default=0)
    send_limit = models.IntegerField(_(u'发信功能限制'), choices=SEND_LIMIT, default=1)
    recv_limit = models.IntegerField(_(u'收信功能限制'), choices=RECV_LIMIT, default=1)
    is_limit_send = models.BooleanField(_(u'限制发送频率'), default=1)

    # 登录方式限制
    is_pop = models.BooleanField(_(u'POP/POPS邮箱收取功能'), default=1)
    is_smtp = models.BooleanField(_(u'SMTP/SMTPS客户端邮件发送功能'), default=1)
    is_imap = models.BooleanField(_(u'IMAP/IMAPS客户端邮件收发功能'), default=1)

    # 密码规则
    is_passwd = models.BooleanField(_(u'定期密码修改设置'), default=1)
    passwd_day = models.IntegerField(_(u'密码有效期'), default=0, help_text=_(u"0代表永远有效，大于0代表多少天密码过期后会强制用户修改密码"))
    passwd_start = models.DateTimeField(_(u"密码有效开始时间"), null=True, blank=True) #, help_text=_(u"不能大于当前时间"))
    is_passwd_first = models.BooleanField(_(u'首次登录修改密码'), default=1)
    passwd_type = models.IntegerField(u'密码组成字符种类', choices=PASSWD_TYPE, default=2, help_text=_(u"密码组成字符包括四种：数字、大写字母、小写字母、特殊字符"))
    passwd_other = models.TextField(_(u"其他密码规则设置"), null=True, blank=True)

    # 反垃圾/反病毒
    is_virus = models.BooleanField(_(u'反病毒功能'), default=1)
    is_spam = models.BooleanField(_(u'反垃圾功能'), default=1)
    is_spf = models.BooleanField(_(u'SPF检测'), default=0)
    is_grey = models.BooleanField(_(u'灰名单检测'), default=0)
    check_attach = models.TextField(_(u"检查附件"), null=True, blank=True)
    match_black = models.TextField(_(u"匹配黑名单"), null=True, blank=True)
    check_spam = models.TextField(_(u"反垃圾引擎"), null=True, blank=True)
    is_formt = models.BooleanField(_(u'检查发件人格式'), default=1, help_text=_(u"此选项不会作用于“本域进站邮件” "))
    spam_folder = models.CharField(_(u'垃圾邮件投递位置'), default='spam', choices=SPAM_FOLDER, max_length=10)
    spam_subject_flag = models.CharField(_(u'垃圾邮件主题标识'), null=True, blank=True, max_length=200)
    isolate_day = models.IntegerField(_(u'隔离邮件保存天数'), default=15)
    is_send_isolate = models.BooleanField(_(u"发送隔离报告"), default=0)
    send_isolate_name = models.CharField(_(u"隔离报告发件人"), null=True, blank=True, max_length=100)
    isolate_url = models.CharField(_(u'隔离报告链接地址'), null=True, blank=True, max_length=200,
                                   help_text=u" “链接地址”必须为类似“mail.example.com“或“114.114.114.114“这种可以通过外网点击访问的地址。如果是“127.0.0.1“,“192.168.xx.xx“这种地址，会导致外网登录的用户无法通过链接操作隔离邮件。 ")
    check_object = models.TextField(_(u"检测对象"), null=True, blank=True)
    check_local = models.TextField(_(u"本域进站邮件"), null=True, blank=True, help_text=_(u"“反垃圾功能”和“反病毒功能”开启后，这里对应的勾选框才会生效"))
    check_outside = models.TextField(_(u"外域进站邮件"), null=True, blank=True, help_text=u"“反垃圾功能”和“反病毒功能”开启后，这里对应的勾选框才会生效")

    # 账号设置
    is_info = models.BooleanField(_(u'个人资料功能'), default=0, help_text=_(u"关闭此功能后用户无法修改个人资料"))
    is_passwd_mdf = models.BooleanField(_(u'密码修改功能'), default=1, help_text=_(u"关闭此功能后用户无法修改邮箱密"))
    is_param = models.BooleanField(_(u'参数设置功能'), default=1)
    is_signature = models.BooleanField(_(u'邮件签名功能'), default=1)
    is_autoreply = models.BooleanField(_(u'自动回复功能'), default=1)
    is_autotans = models.BooleanField(_(u'自动转发功能'), default=1, help_text=_(u"全局自动转发开闭开关，除此之外，每个邮箱用户也有单独开启自动转发开关，在邮箱账号管理中设置"))
    is_blackwhite = models.BooleanField(_(u'黑白名单功能'), default=1)
    is_tansdefault = models.BooleanField(_(u'设置自动转发默认值'), default=1, help_text=_(u"选择“是”，在后台邮件账户管理中，用户是否可以自行设置自动转发的默认值是“是”，否则为“否”"))
    is_move = models.BooleanField(_(u'邮箱搬家功能'), default=1)
    is_suggest = models.BooleanField(_(u'邮箱意见反馈功能'), default=1)
    is_view = models.BooleanField(_(u'邮件召回记录查看'), default=1)
    is_filter = models.BooleanField(_(u'邮件过滤功能'), default=1)
    is_smtp_tans = models.BooleanField(_(u'SMTP外发邮件中转'), default=1)

    # 账号密级
    passwd_level = models.IntegerField(_(u"账号密级"), default=1, choices=PASSWD_LEVEL)

    class Meta:
        managed = False
        db_table = 'core_group'
        verbose_name = _(u'组权限')
        verbose_name_plural = _(u'组权限')
        unique_together = (
            ('domain_id', 'name'),
        )

    @property
    def domain(self):
        obj = Domain.objects.filter(id=self.domain_id).first()
        return obj and obj.domain or None

    def delete(self, using=None, keep_parents=False):
        CoreGroupMember.objects.filter(group_id=self.id).delete()
        super(CoreGroup, self).delete(using=using, keep_parents=keep_parents)

class CoreGroupMember(models.Model):
    group = models.ForeignKey(CoreGroup, related_name='group_member')
    address = models.CharField(_(u'邮箱'), max_length=200, null=True, blank=True)
    name = models.CharField(_(u'姓名'), max_length=80, null=True, blank=True)
    remark = models.TextField(_(u'备注'), blank=True, null=True)
    created = models.DateTimeField(_(u'添加时间'), auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'core_group_member'
        verbose_name = _(u'组权限成员表')
        verbose_name_plural = _(u'组权限成员表')
        unique_together = (
            ('group', 'address'),
        )

    def set_name(self):
        obj = Mailbox.objects.filter(mailbox=self.address).first()
        self.name = obj and obj.name or None






