# coding=utf-8
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from auditlog.registry import auditlog


def save_login_log(sender, user, request, **kwargs):
    agent = request.META.get('HTTP_USER_AGENT', None)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    CoreLog.objects.create(customer=user, action='user_login', ip=ip, desc=u'浏览器信息：{}'.format(agent))
    return

user_logged_in.connect(save_login_log)

from django.utils.translation import ugettext_lazy as _

TRUE_OR_FALSE = (
    (True, u'是'),
    (False, u'否'),
)

DEPLOY_STATUS = (
    ('normal', u'正常'),
    ('fail', u'部署失败'),
    ('success', u'部署成功'),
    ('waiting', u'等待部署'),
    ('helo_waiting', u'helo等待部署'),
    ('deploying', u'部署中'),
    ('helo_deploying', u'helo部署中')
)

IPPOOL_TYPE = (
    ('auto', u'自动池'),
    ('backup', u'备用池'),
    ('manual', u'手动池'),
)

CUSTOMER_STATUS = (
    ('', _(u'--')),
    ('normal', _(u'正常')),
    ('expiring', _(u'即将过期')),
    ('expired', _(u'已过期')),
    ('disabled', _(u'已禁用'))
)


ROUTERULE_TYPE = (
    ('domain', u'目标域名'),
    ('keyword', u'关键字')
)

CUSTOMER_TYPE = (
    ('', '--'),
    ('relay', u'中继'),
    ('collect', u'网关'),
    ('all', u'全部(中继/网关)')
)

CHECK_LEVEL = (
    ('', '--'),
    ('basic', u'基础反垃圾'),
    ('intermediate', u'中级反垃圾'),
    ('senior', u'高级反垃圾'),
)

NOTIFICATION_TYPE = (
    ('', u'无'),
    ('bulk', u'群发邮件通知'),
    ('review', u'审核邮件通知'),
)

ACTION_TYPE = (
    ('user_login', _(u'登录日志')),
)


class IpPool(models.Model):
    """
    IP发送池
    """
    name = models.CharField(u'名称', max_length=20, null=False, blank=False, help_text=u'发送池名称,如普通池1, 备份池')
    type = models.CharField(u'发送池类型', max_length=10, choices=IPPOOL_TYPE)
    desp = models.TextField(u'描述', null=True, blank=True)

    def __unicode__(self):
        return self.name

class Manager(models.Model):
    username = models.CharField(_('username'), max_length=30, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)

    class Meta:
        db_table = 'auth_user'

class Customer(AbstractBaseUser):
    username = models.CharField(u'客户帐号', max_length=50, null=False, blank=False, unique=True)
    # password = models.CharField(u'密码', max_length=128, null=True, blank=True)
    company = models.CharField(_(u'公司名称'), max_length=100, null=False, blank=False, unique=True)
    service_start = models.DateField(u'服务开始时间')
    service_end = models.DateField(u'服务到期时间')
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    disabled = models.BooleanField(u'是否禁用', default=False, choices=TRUE_OR_FALSE)
    status = models.CharField(u'状态', max_length=10, default="normal", choices=CUSTOMER_STATUS)
    ip_pool = models.ForeignKey(IpPool, null=True, blank=True, verbose_name=u'分配IP发送池', on_delete=models.SET_NULL)
    support_id = models.CharField(u'客户服务平台对接字段', max_length=50, null=True, blank=True)
    type = models.CharField(u'客户类型', max_length=10, null=True, blank=True, choices=CUSTOMER_TYPE)
    contact = models.CharField(_(u'联系人'), max_length=20, null=True, blank=True)
    mobile = models.CharField(_(u'联系人手机'), max_length=20, null=True, blank=True)
    email = models.EmailField(_(u'邮箱'), max_length=20, null=True, blank=True)
    emergency_contact = models.CharField(_(u'紧急联系人'), max_length=20, null=True, blank=True)
    emergency_mobile = models.CharField(_(u'紧急联系人手机'), max_length=20, null=True, blank=True)
    gateway_service_start = models.DateField(u'网关服务开始时间', null=True, blank=True)
    gateway_service_end = models.DateField(u'网关服务到期时间', null=True, blank=True)
    collect_limit = models.IntegerField(u'网关用户数(收件人)', default=0)
    gateway_status = models.CharField(u'网关状态', max_length=10, default="normal", choices=CUSTOMER_STATUS)
    lang_code = models.CharField(u'用户语言', max_length=10, choices=settings.LANGUAGES, default='zh-cn', null=False, blank=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def get_short_name(self):
        return self.username

    def get_username(self):
        return self.username

    def is_super(self):
        return False

    def is_relay(self):
        return self.type in ['relay', 'all']

    def is_collect(self):
        return self.type in ['collect', 'all']

    @property
    def customer_setting(self):
        s, _ = CustomerSetting.objects.get_or_create(customer=self)
        return s

    def __unicode__(self):
        return u'{}({})'.format(self.company, self.username)

    def save(self, *args, **kwargs):
        disabled = True if self.status == 'disabled' else False
        CustomerIp.objects.filter(customer_id=self.id).update(disabled=disabled)
        CustomerDomain.objects.filter(customer_id=self.id).update(disabled=disabled)
        CustomerMailbox.objects.filter(customer_id=self.id).update(disabled=disabled)
        super(Customer, self).save(*args, **kwargs)


class CustomerIp(models.Model):
    customer = models.ForeignKey(Customer, related_name='ip')
    ip = models.CharField(u'客户固定ip', max_length=20, null=False, blank=False)
    disabled = models.BooleanField(u'是否禁用', default=False)

    def __unicode__(self):
        return self.ip


class CustomerDomain(models.Model):
    customer = models.ForeignKey(Customer, related_name='domain')
    domain = models.CharField(u'客户信任发送域名', max_length=100, null=False, blank=False)
    disabled = models.BooleanField(u'是否禁用', default=False)

    def save(self, *args, **kwargs):
        self.domain = self.domain.lower()
        super(CustomerDomain, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.domain


class ColCustomerDomain(models.Model):
    """
    网关： 域名-转发地址 对应关系
    """
    customer = models.ForeignKey(Customer, related_name='col_domain')
    domain = models.CharField(u'客户域名', max_length=100, null=False, blank=False)
    forward_address = models.CharField(u'转发地址', max_length=100, null=False, blank=False)
    disabled = models.BooleanField(u'是否禁用', default=False)

    def save(self, *args, **kwargs):
        self.domain = self.domain.lower()
        super(ColCustomerDomain, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.domain


class CustomerMailbox(models.Model):
    customer = models.ForeignKey(Customer, related_name='mailbox')
    mailbox = models.CharField(u'邮箱帐号', max_length=100, null=False, blank=False)
    password = models.CharField(u'邮箱密码', max_length=100, null=False, blank=False)
    disabled = models.BooleanField(u'是否禁用', default=False)

    def __unicode__(self):
        return "{}----{}".format(self.mailbox, self.password)


class Cluster(models.Model):
    """
    群发SMTP机器
    """
    name = models.CharField(u'SMTP主机名', max_length=50, null=False, blank=False, help_text=u'如：电信-1')
    ip = models.GenericIPAddressField(u'SMTP主机IP', null=False, blank=False, help_text=u'如：192.168.1.188')
    # ip = models.CharField(u'IP地址', max_length=100, null=False, blank=False, unique=True)
    port = models.IntegerField(u'sshd端口', default=22, null=False, blank=False)
    api_url = models.URLField(u'API地址', max_length=150, null=True, blank=True,
                              help_text=u'默认为：http://主机IP:10001/state/')
    description = models.TextField(u'描述', null=True, blank=True)
    username = models.CharField(u'用户名', max_length=50, null=False, blank=False)
    password = models.CharField(u'密码', max_length=100, null=False, blank=False, help_text=u'密码将会明文显示')
    deploy_status = models.CharField(u'部署状态', max_length=50, default='normal', choices=DEPLOY_STATUS)
    deploy_dtm = models.DateTimeField(u'最近部署时间', auto_now=False, auto_now_add=False, null=True)
    deploy_info = models.TextField(u'部署结果', max_length=2000, null=True, blank=True)
    create_dtm = models.DateTimeField(u'添加时间', auto_now_add=True)

    def __unicode__(self):
        return self.name


class ClusterIp(models.Model):
    """
    SMTP服务器Ip/helo 配置
    """
    cluster = models.ForeignKey(Cluster, related_name='cluster')
    # ip = models.GenericIPAddressField(u'IP地址', null=False, blank=False, unique=True)
    ip = models.CharField(u'IP地址', max_length=100, null=False, blank=False, unique=True)
    device = models.CharField(u'设备名', max_length=100, null=False, blank=False, help_text=u'参考: eth0 [最后一位是数字零]')
    netmask = models.CharField(u'子网掩码', max_length=255, null=False, blank=False, help_text=u'参考: 255.255.255.0.')
    helo = models.CharField(u'helo', max_length=200, null=False, blank=False)
    disabled = models.BooleanField(u'是否禁用', default=False, choices=TRUE_OR_FALSE)
    ip_pool = models.ForeignKey(IpPool, null=True, blank=True, verbose_name=u'分配IP发送池', on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.ip


class RouteRule(models.Model):
    """
    路由规则
    """
    ip_pool = models.ForeignKey(IpPool, null=False, blank=False, verbose_name=u'发送池')
    type = models.CharField(u'类型', max_length='10', default='domain', choices=ROUTERULE_TYPE)
    domain = models.CharField(u'目标域名', max_length=100, null=True, blank=True, help_text=u'一个或多个目标域名的邮件从某个地址池发送')
    keyword = models.CharField(u'关键字', max_length=100, null=True, blank=True,
                               help_text=u'日志中含有某些关键词的邮件（地址池全部IP发送出错）从某个地址池发送')
    disabled = models.BooleanField(u'是否禁用', default=False, choices=TRUE_OR_FALSE)


class CustomerSetting(models.Model):
    """
    用户设置
    """
    customer = models.ForeignKey(Customer)
    bounce = models.BooleanField(_(u'中继:开启退信'), default=False)
    bigmail = models.BooleanField(_(u'中继:超大邮件自动转网络链接发送'), default=False ,
                                  help_text=_(u'如果开启：发送后日志显示邮件超大满的邮件，则自动转链接方式（发送一次，如果还不成功则不尝试），附件保留在服务器上，附件保留时间为X天。'))
    transfer_max_size = models.IntegerField(_(u'中继：自动转网络附件最大阀值'), default=0, help_text=_(u'单位：M，邮件大小超过该阀值，则该邮件发送时自动转网络附件, 默认值０, 表示用系统默认设置值'))
    replace_sender = models.BooleanField(u'中继:是否替换真实发件人，如果开启,自动把from头改成真实的发件人', default=False)
    notice = models.BooleanField(_(u'短信/邮件消息通知开关'), default=True, help_text=_(u'选中即为开启，当关闭时，该用户账号不发短信/邮件通知'))
    check_autoreply = models.BooleanField(u'中继过滤:自动回复', default=True, help_text=u'选中即为开启，开启表示过滤"自动回复"邮件,默认开启')
    can_view_mail = models.BooleanField(_(u'用户是否可以查看邮件'), default=False)
    c_bounce = models.BooleanField(u'网关:开启退信', default=False, help_text=u'选中即为开启,开启表示网关邮件出站失败(邮件不存在,超大/满,拒收),系统会自动退信')
    spamrpt = models.BooleanField(_(u'网关：是否开启垃圾邮件隔离报告开关'), default=False, help_text=_(u'选中时为开启,会将被拒绝的邮件以报告的形式发送给该用户,默认每天零点发上一天的邮件；当关闭时，不会发送被拒绝的邮件给用户'))
    m_spamrpt = models.BooleanField(_(u'网关：是否开启垃圾邮件隔离报告开关(对管理员）'), default=False, help_text=_(u'选中时为开启,会将被拒绝的邮件以报告的形式发送给管理员,默认每天零点发上一天的邮件；当关闭时，不会发送被拒绝的邮件给管理员'))
    interval_spamrpt = models.IntegerField(u'网关:隔离报告发送间隔', default=0, help_text=u'单位小时，每X个小时发送X小时以前的隔离报告内容')
    is_spamrpt_sendtime = models.BooleanField(u'是否自定义隔离报告发送时间', default=False)
    spamrpt_sendtime = models.TimeField(u'隔离报告发送时间', null=True, blank=True, help_text=u'将该时间以前的24个小时内所有的拒绝邮件，以报告形式在该时间发送，而且不会在默认的零点发送了')
    check_level = models.CharField(_(u'网关过滤级别'), max_length=20, default='intermediate', choices=CHECK_LEVEL)
    check_spf = models.BooleanField(_(u'网关过滤:spf'), default=False)
    check_rbl = models.BooleanField(_(u'网关过滤:rbl'), default=False)
    check_format = models.BooleanField(u'网关过滤:发件人格式检测', default=True)
    check_dspam = models.BooleanField(_(u'网关过滤:dspam'), default=True)
    check_ctasd = models.BooleanField(_(u'网关过滤:cyber'), default=True)
    check_sender = models.BooleanField(_(u'网关过滤:发件人黑名单'), default=True)
    check_subject = models.BooleanField(_(u'网关过滤:主题关键字'), default=True)
    check_content = models.BooleanField(_(u'网关过滤:内容关键字'), default=True)
    check_spam = models.BooleanField(_(u'网关过滤:spamassassion'), default=True)
    check_high_risk = models.BooleanField(_(u'网关过滤:高危邮件'), default=True)
    service_notice = models.BooleanField(u'服务到期通知开关', default=False, help_text=u'选中即为开启，当关闭时，该用户账号不发服务到期邮件通知')


class MyPermission(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    permission = models.ForeignKey(Permission, null=True, blank=True)
    name = models.CharField(u'权限名称', max_length=20, unique=True, null=False, blank=False, help_text=u'请使用英文名称')
    is_nav = models.BooleanField(u'是否为导航', default=True)
    nav_name = models.CharField(u'导航名称', max_length=20, null=False, blank=False, help_text=u'如果不是导航，可不用填写')
    url = models.CharField(u'目录url', max_length=150, null=True, blank=True)
    is_default = models.BooleanField(u'是否为默认权限', default=False, help_text=u'如果是默认权限，添加后不能通过页面修改')
    order = models.IntegerField(u'导航顺序', default=1, help_text=u'越小排在越前面')

    def __unicode__(self):
        return u'{}({})'.format(self.name, self.nav_name)

    def per(self):
        permission = self.permission
        return '{}.{}'.format(permission.content_type.app_label, permission.codename)

    def nav_children(self):
        return self.children.filter(is_nav=True)

    def save(self, *args, **kwargs):
        if not self.permission:
            content_type = ContentType.objects.get(app_label='core', model='mypermission')
            permission, _ = Permission.objects.get_or_create(codename=self.name,
                                                             name=self.name,
                                                             content_type=content_type)
            setattr(self, 'permission', permission)
        super(MyPermission, self).save(*args, **kwargs)


class PostfixStatus(models.Model):
    date = models.DateField(u'日期')
    connect_num = models.IntegerField(u'连接数', default=0)
    mail_num = models.IntegerField(u'邮件总数', default=0)
    reject_num = models.IntegerField(u'拒绝数', default=0)
    pass_num = models.IntegerField(u'中转数', default=0)
    rate1 = models.IntegerField(u'限制规则１', default=0)
    rate2 = models.IntegerField(u'限制规则2', default=0)
    rate3 = models.IntegerField(u'限制规则3', default=0)
    rate4 = models.IntegerField(u'限制规则4', default=0)
    spf = models.IntegerField(u'spf', default=0)
    rbl = models.IntegerField(u'rbl', default=0)
    update = models.DateTimeField(u'更新时间', auto_now=True)



class Notification(models.Model):
    subject = models.CharField(u'通知主题', max_length=50, null=True)
    content = models.TextField(u'通知内容')
    type = models.CharField(u'通知类型', max_length=10, choices=NOTIFICATION_TYPE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, help_text=u'通知的客户对象')
    # manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text=u'通知的管理员对象')
    is_read = models.BooleanField(u'是否阅读', default=False, help_text=u'通知是否阅读')
    is_notice = models.BooleanField(u'是否发站内通知', default=False)
    is_sms = models.BooleanField(u'是否发短信通知', default=False)
    is_email = models.BooleanField(u'是否发邮件通知', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

class UrlRemark(models.Model):
    url = models.CharField(u'URL', max_length=200, null=False, blank=False, unique=True, help_text=u'url地址')
    remark = models.TextField(u'备注', null=True, blank=True)
    create_time = models.DateTimeField(u'创建日期', auto_now_add=True)
    write_time = models.DateTimeField(u'更新时间', auto_now=True)

class CoreLog(models.Model):
    " 操作日志列表 "
    datetime = models.DateTimeField(u'操作时间', auto_now_add=True)
    manager = models.ForeignKey(Manager, null=True, blank=True, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING)
    action = models.CharField(u'操作类型', max_length=20, null=True, blank=True, choices=ACTION_TYPE, db_index=True)
    desc = models.TextField(u'说明')
    ip = models.CharField(u'操作IP', max_length=15, null=True, blank=True)

class CustomerSummary(models.Model):
    """
    客户每天发送状态统计
    """
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True, blank=True)
    date = models.DateField(u'日期')
    relay_count = models.IntegerField(u'中继发件人数量', default=0)
    relay_limit = models.IntegerField(u'中继用户数', default=0)
    is_relay_limit = models.BooleanField(u'中继是否超限', default=0)
    collect_count = models.IntegerField(u'网关收件人数量', default=0)
    collect_limit = models.IntegerField(u'网关用户数', default=0)
    is_collect_limit = models.BooleanField(u'网关是否超限', default=0)
    total_all = models.IntegerField('总共数量', default=0, help_text=u'邮件封数mail_id=0')
    all = models.IntegerField('总共数量', default=0)
    all_flow = models.BigIntegerField('总共流量', default=0)
    out_all = models.IntegerField('出站总共数量', default=0)
    out_all_flow = models.BigIntegerField('出站总共流量', default=0)
    reject = models.IntegerField('过滤总共数量', default=0)
    reject_flow = models.BigIntegerField('过滤总共流量', default=0)
    finished = models.IntegerField('成功总共数量', default=0)
    finished_flow = models.BigIntegerField('成功总共流量', default=0)
    fail_finished = models.IntegerField('失败总共数量', default=0)
    fail_finished_flow = models.BigIntegerField('失败总共流量', default=0)

    c_total_all = models.IntegerField('总共数量', default=0, help_text=u'邮件封数mail_id=0')
    c_all = models.IntegerField('总共数量', default=0)
    c_all_flow = models.BigIntegerField('总共流量', default=0)
    c_out_all = models.IntegerField('出站总共数量', default=0)
    c_out_all_flow = models.BigIntegerField('出站总共流量', default=0)
    c_reject = models.IntegerField('过滤总共数量', default=0)
    c_reject_flow = models.BigIntegerField('过滤总共流量', default=0)
    c_finished = models.IntegerField('成功总共数量', default=0)
    c_finished_flow = models.BigIntegerField('成功总共流量', default=0)
    c_fail_finished = models.IntegerField('失败总共数量', default=0)
    c_fail_finished_flow = models.BigIntegerField('失败总共流量', default=0)



auditlog.register(Customer, exclude_fields=['creater', 'operater', 'operate_time', 'is_webmail', 'relay_exceed',
                                            'collect_exceed'])
