# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import Permission
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from auditlog.registry import auditlog


def user_unicode(self):
    return self.last_name
    #return u'%s%s' % (self.first_name, self.last_name)


User.__unicode__ = user_unicode

admin.site.unregister(User)
admin.site.register(User)

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
    ('', u'--'),
    ('normal', u'正常'),
    ('expiring', u'即将过期'),
    ('expired', u'已过期'),
    ('disabled', u'已禁用')

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
    ('', u'--'),
    ('basic', u'基础反垃圾'),
    ('intermediate', u'中级反垃圾'),
    ('senior', u'高级反垃圾'),
)

MAIL_SERVERS = (
    ('shenzhen', u'深圳'),
    ('hangzhou', u'杭州'),
)

NOTIFICATION_TYPE = (
    ('', u'无'),
    ('bulk', u'违规邮件通知'),
    ('review', u'审核邮件通知'),
    ('ip', u'发送机IP不通通知'),
    ('jam', u'服务器拥堵通知'),
    ('collect', u'网关用户超过限制通知'),
    ('relay', u'中继用户超过限制通知'),
    ('c_service', u'网关服务到期提醒'),
    ('r_service', u'中继服务到期提醒'),
    ('s_warning', u'中继发件人提醒'),
    ('c_down', u'网关客户服务器DOWN机通知'),
)

ACTION_TYPE = (
    ('user_login', u'登录日志'),
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


class Customer(AbstractBaseUser):
    username = models.CharField(u'客户帐号', max_length=50, null=False, blank=False, unique=True)
    # password = models.CharField(u'密码', max_length=128, null=True, blank=True)
    company = models.CharField(u'公司名称', max_length=100, null=False, blank=False, unique=True)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)
    disabled = models.BooleanField(u'是否禁用', default=False, choices=TRUE_OR_FALSE)
    ip_pool = models.ForeignKey(IpPool, null=True, blank=True, verbose_name=u'分配IP发送池', on_delete=models.SET_NULL)
    support_id = models.CharField(u'客户服务平台对接字段', max_length=50, null=True, blank=True)
    support_name = models.CharField(u'客户支持名称', max_length=50, null=True, blank=True)
    support_email = models.CharField(u'客户支持邮箱', max_length=50, null=True, blank=True)
    type = models.CharField(u'客户类型', max_length=10, null=True, blank=True, choices=CUSTOMER_TYPE)
    contact = models.CharField(u'联系人', max_length=100, null=True, blank=True)
    mobile = models.CharField(u'联系人手机', max_length=20, null=True, blank=True)
    email = models.EmailField(u'邮箱', max_length=50, null=True, blank=True)
    emergency_contact = models.CharField(u'紧急联系人', max_length=20, null=True, blank=True)
    emergency_mobile = models.CharField(u'紧急联系人手机', max_length=20, null=True, blank=True)
    creater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creater22')
    operater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operater22')
    operate_time = models.DateTimeField(u'最后操作日期', null=True, auto_now=True)
    # last_login = models.DateTimeField(u'最后登录时间', blank=True, null=True)
    manager = models.ForeignKey(User, related_name='c_manager', null=True, blank=True, on_delete=models.SET_NULL)
    service_start = models.DateField(u'中继服务开始时间', null=True, blank=True)
    service_end = models.DateField(u'中继服务到期时间', null=True, blank=True)
    relay_limit = models.IntegerField(u'中继用户数(发件人)', default=0)
    relay_exceed = models.IntegerField(u'中继超限次数', default=0)
    status = models.CharField(u'中继状态', max_length=10, default="normal", choices=CUSTOMER_STATUS)
    gateway_service_start = models.DateField(u'网关服务开始时间', null=True, blank=True)
    gateway_service_end = models.DateField(u'网关服务到期时间', null=True, blank=True)
    collect_limit = models.IntegerField(u'网关用户数(收件人)', default=0)
    collect_exceed = models.IntegerField(u'网关超限次数', default=0)
    gateway_status = models.CharField(u'网关状态', max_length=10, default="normal", choices=CUSTOMER_STATUS)
    tech = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='tech', null=True, blank=True)
    sale = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='sale', null=True, blank=True)
    service = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='service', null=True, blank=True)
    lang_code = models.CharField(u'用户语言', max_length=10, choices=settings.LANGUAGES, default='zh-cn', null=False,
                                 blank=False)
    is_webmail = models.BooleanField(u'是否为邮件系统', default=0)

    def __unicode__(self):
        return u'{}({})'.format(self.company, self.username)

    def save(self, *args, **kwargs):
        disabled = True if self.status == 'disabled' else False
        CustomerIp.objects.filter(customer_id=self.id).update(disabled=disabled)
        CustomerDomain.objects.filter(customer_id=self.id).update(disabled=disabled)
        CustomerMailbox.objects.filter(customer_id=self.id).update(disabled=disabled)
        disabled = True if self.gateway_status == 'disabled' else False
        ColCustomerDomain.objects.filter(customer_id=self.id).update(disabled=disabled)
        super(Customer, self).save(*args, **kwargs)

    @property
    def customer_setting(self):
        s, _ = CustomerSetting.objects.get_or_create(customer=self)
        return s

    @property
    def customer_localized_setting(self):
        s, _ = CustomerLocalizedSetting.objects.get_or_create(customer=self)
        return s

    class Meta:
        verbose_name = u'客户信息'


class CustomerIp(models.Model):
    customer = models.ForeignKey(Customer, related_name='ip')
    ip = models.CharField(u'客户固定ip', max_length=20, null=False, blank=False)
    disabled = models.BooleanField(u'是否禁用', default=False)

    def __unicode__(self):
        return self.ip

    class Meta:
        verbose_name = u'中继信任IP'


class CustomerDomain(models.Model):
    customer = models.ForeignKey(Customer, related_name='domain')
    domain = models.CharField(u'客户信任发送域名', max_length=100, null=False, blank=False)
    disabled = models.BooleanField(u'是否禁用', default=False)

    def save(self, *args, **kwargs):
        self.domain = self.domain.lower()
        super(CustomerDomain, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.domain

    class Meta:
        verbose_name = u'中继信任域名'


class ColCustomerDomain(models.Model):
    """
    网关： 域名-转发地址 对应关系
    """
    customer = models.ForeignKey(Customer, related_name='col_domain')
    domain = models.CharField(u'客户域名', max_length=100, null=False, blank=False)
    forward_address = models.CharField(u'转发地址', max_length=100, null=False, blank=False)
    port = models.IntegerField(u'转发端口', default=25)
    is_ssl = models.BooleanField(u'是否加密', default=False)
    priority = models.SmallIntegerField(u'优先级', default=0)
    disabled = models.BooleanField(u'是否禁用', default=False)

    def save(self, *args, **kwargs):
        self.domain = self.domain.lower()
        super(ColCustomerDomain, self).save(*args, **kwargs)

    def __unicode__(self):
        return "{}----{}".format(self.domain, self.forward_address)

    class Meta:
        verbose_name = u'网关信任域名'


class CustomerMailbox(models.Model):
    customer = models.ForeignKey(Customer, related_name='mailbox')
    mailbox = models.CharField(u'邮箱帐号', max_length=100, null=False, blank=False)
    password = models.CharField(u'邮箱密码', max_length=100, null=False, blank=False)
    disabled = models.BooleanField(u'是否禁用', default=False)

    def __unicode__(self):
        return "{}----{}".format(self.mailbox, self.password)

    class Meta:
        verbose_name = u'中继帐号'


class Cluster(models.Model):
    """
    群发SMTP机器
    """
    name = models.CharField(u'SMTP主机名', max_length=50, null=False, blank=False, help_text=u'如：电信-1')
    # ip = models.GenericIPAddressField(u'SMTP主机IP', null=False, blank=False, help_text=u'如：192.168.1.188')
    ip = models.CharField(u'SMTP主机IP', max_length=100, null=False, blank=False, unique=True)
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
    customer = models.ForeignKey(Customer, unique=True)
    bounce = models.BooleanField(u'中继:开启退信', default=False)
    bigmail = models.BooleanField(u'中继:超大邮件自动转网络链接发送', default=False,
                                  help_text=u'如果开启：发送后日志显示邮件超大满的邮件，则自动转链接方式（发送一次，如果还不成功则不尝试），附件保留在服务器上，附件保留时间为X天。')
    transfer_max_size = models.IntegerField(u'中继：自动转网络附件最大阀值', default=0,
                                            help_text=u'单位：M，邮件大小超过该阀值，则该邮件发送时自动转网络附件, 默认值０, 表示用系统默认设置值')
    replace_sender = models.BooleanField(u'中继:是否替换真实发件人，如果开启,自动把from头改成真实的发件人', default=False)
    notice = models.BooleanField(u'短信/邮件消息通知开关', default=True, help_text=u'选中即为开启，当关闭时，该用户账号不发短信/邮件通知')
    service_notice = models.BooleanField(u'服务到期通知开关', default=False, help_text=u'选中即为开启，当关闭时，该用户账号不发服务到期邮件通知')
    check_autoreply = models.BooleanField(u'中继过滤:自动回复', default=True, help_text=u'选中即为开启，开启表示过滤"自动回复"邮件,默认开启')
    can_view_mail = models.BooleanField(u'用户是否可以查看邮件', default=False)
    c_bounce = models.BooleanField(u'网关:开启退信', default=False, help_text=u'选中即为开启,开启表示网关邮件出站失败(邮件不存在,超大/满,不重试),系统会自动退信')
    spamrpt = models.BooleanField(u'网关：是否开启垃圾邮件隔离报告开关', default=False,
                                  help_text=u'选中时为开启,会将被拒绝的邮件以报告的形式发送给该用户,默认每天零点发上一天的邮件；当关闭时，不会发送被拒绝的邮件给用户')
    m_spamrpt = models.BooleanField(u'网关：是否开启垃圾邮件隔离报告开关(对管理员）', default=False,
                                    help_text=u'选中时为开启,会将被拒绝的邮件以报告的形式发送给管理员,默认每天零点发上一天的邮件；当关闭时，不会发送被拒绝的邮件给管理员')
    interval_spamrpt = models.IntegerField(u'网关:隔离报告发送间隔', default=0, help_text=u'单位小时，每X个小时发送X小时以前的隔离报告内容')
    is_spamrpt_sendtime = models.BooleanField(u'是否自定义隔离报告发送时间', default=False)
    spamrpt_sendtime = models.TimeField(u'隔离报告发送时间', null=True, blank=True, help_text=u'将该时间以前的24个小时内所有的拒绝邮件，以报告形式在该时间发送，而且不会在默认的零点发送了')
    check_level = models.CharField(u'网关过滤级别', max_length=20, default='intermediate', choices=CHECK_LEVEL)
    check_spf = models.BooleanField(u'网关过滤:spf', default=False)
    check_rbl = models.BooleanField(u'网关过滤:rbl', default=False)
    check_format = models.BooleanField(u'网关过滤:发件人格式检测', default=True)
    check_dspam = models.BooleanField(u'网关过滤:dspam', default=True)
    check_ctasd = models.BooleanField(u'网关过滤:cyber', default=True)
    check_sender = models.BooleanField(u'网关过滤:发件人黑名单', default=True)
    check_subject = models.BooleanField(u'网关过滤:主题关键字', default=True)
    check_content = models.BooleanField(u'网关过滤:内容关键字', default=True)
    check_spam = models.BooleanField(u'网关过滤:spamassassion', default=True)
    check_high_risk = models.BooleanField(u'网关过滤:高危邮件', default=True)


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
    rate1 = models.IntegerField(u'限制规则１(20分钟)', default=0)
    rate2 = models.IntegerField(u'限制规则2(30分钟)', default=0)
    rate3 = models.IntegerField(u'限制规则3(1小时)', default=0)
    rate4 = models.IntegerField(u'限制规则4(3小时)', default=0)
    rate5 = models.IntegerField(u'限制规则5(10分钟)', default=0)
    rate6 = models.IntegerField(u'限制规则6(6小时)', default=0)
    rate7 = models.IntegerField(u'限制规则7(12小时)', default=0)
    rate8 = models.IntegerField(u'限制规则8(24小时)', default=0)
    spf = models.IntegerField(u'spf', default=0)
    rbl = models.IntegerField(u'rbl', default=0)
    update = models.DateTimeField(u'更新时间', auto_now=True)
    server_id = models.CharField(u'所在服务器的ID', max_length=20, default='shenzhen', choices=MAIL_SERVERS,
                                 db_index=True)


class Notification(models.Model):
    subject = models.CharField(u'通知主题', max_length=50, null=True)
    content = models.TextField(u'通知内容')
    type = models.CharField(u'通知类型', max_length=10, choices=NOTIFICATION_TYPE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, help_text=u'通知的客户对象')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text=u'通知的管理员对象',
                                related_name='notification_manager')
    is_read = models.BooleanField(u'是否阅读', default=False, help_text=u'通知是否阅读')
    is_notice = models.BooleanField(u'是否发站内通知', default=False)
    is_sms = models.BooleanField(u'是否发短信通知', default=False)
    is_email = models.BooleanField(u'是否发邮件通知', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    def is_notice_display(self):
        return CustomerSetting.objects.filter(customer=self.customer, notice=True) if self.customer else True


class ProfileBase(type):
    def __new__(cls, name, bases, attrs):  # 构造器，（名字，基类，类属性）
        module = attrs.pop('__module__')
        parents = [b for b in bases if isinstance(b, ProfileBase)]
        if parents:
            fields = []
            for obj_name, obj in attrs.items():
                if isinstance(obj, models.Field): fields.append(obj_name)
                User.add_to_class(obj_name, obj)  # ###最重要的步骤
            UserAdmin.fieldsets = list(UserAdmin.fieldsets)
            UserAdmin.fieldsets.append((name, {'fields': fields}))
        return super(ProfileBase, cls).__new__(cls, name, bases, attrs)


class ProfileUser(object):
    __metaclass__ = ProfileBase


class ExtraInfo(ProfileUser):
    phone_number = models.CharField(max_length=20, verbose_name=u'电话号码', null=True, blank=True)


class UrlRemark(models.Model):
    url = models.CharField(u'URL', max_length=200, null=False, blank=False, unique=True, help_text=u'url地址')
    remark = models.TextField(u'备注', null=True, blank=True)
    create_uid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="urlremark_user1")
    create_time = models.DateTimeField(u'创建日期', auto_now_add=True)
    write_uid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name="urlremark_user2")
    write_time = models.DateTimeField(u'更新时间', auto_now=True)


class CustomerLocalizedSetting(models.Model):
    """
    用户设置
    """
    customer = models.ForeignKey(Customer, unique=True)
    token = models.CharField(u'访问权限Token', max_length=50, null=True, blank=True)
    ip = models.CharField(u'客户ip', max_length=20, null=False, blank=False)
    port = models.IntegerField(u'端口', default=10000)


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





class CoreLog(models.Model):
    " 操作日志列表 "
    datetime = models.DateTimeField(u'操作时间', auto_now_add=True)
    manager = models.ForeignKey(User, null=True, blank=True, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING)
    action = models.CharField(u'操作类型', max_length=20, null=True, blank=True, choices=ACTION_TYPE, db_index=True)
    desc = models.TextField(u'说明')
    ip = models.CharField(u'操作IP', max_length=15, null=True, blank=True)


auditlog.register(Customer, exclude_fields=['creater', 'operater', 'operate_time', 'is_webmail', 'relay_exceed',
                                            'collect_exceed'])
auditlog.register(CustomerIp, exclude_fields=['customer'], relate_field='customer')
auditlog.register(CustomerDomain, exclude_fields=['customer'], relate_field='customer')
auditlog.register(CustomerMailbox, exclude_fields=['customer'], relate_field='customer')
auditlog.register(ColCustomerDomain, exclude_fields=['customer'], relate_field='customer')
