# coding=utf-8
from __future__ import unicode_literals
import time
import json
import hashlib
import urllib2
import urllib
import datetime
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.defaultfilters import date as date_format
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from app.core.configs import ( IS_REGISTER_CHOICE, CHOICE_0_1, SERVER_TYPE, SEND_TYPE, SERVICE_TYPE, STATUS, DISABLED, USER_TYPE,
                               ACTION_TYPE, SEX_CHOICES, CUSTOMER_DOMAIN_STATUS, PAY_WAY, ORDER_STATUS, INVOICE_STATUS,
                               INVOICE_TYPE, ESTIMATE_SELECT, CONTENT_SELECT, INDUSTRY_SELECT, WAY_SELECT, WEB_STYLE, AUTOREMOVE_TYPE,
                               DUPLICATE_TYPE, IS_SHEAR_FLAG, NOTIFICATION_TYPE )
from app.template.configs import ENCODING_TYPE, CHARACTER_TYPE, IMAGE_TYPE, ATTACH_TYPE
from lib.tools import get_random_string, get_client_ip
from lib.tools import ZeroDateTimeField
from lib.ipparse import split_ip_to_area_title
from lib.IpSearch import IpSearch
from tagging.models import Tag
from app.core.utils import domainparse
from django.utils.translation import ugettext_lazy as _



class WeixinCustomer(models.Model):
    """
    微信客户
    {u'openid': u'oMaZnwp6MCKAxjBi0anwBsMKf3pw',
     u'access_token': u'8amyiVIWd3Ssafb08HED-8xNIB5DDDsFm6QW-bIwMaKPmFJUFA9X6X7i3rNnazqOTGNeA7jNBs8X8S-4cd9moIMZsKaT0BAFj_LjteX_Yxk',
     u'unionid': u'oh8S_wRSPZ5PfCeFnoDlPV8V1H2M', u'expires_in': 7200, u'scope': u'snsapi_login',
     u'refresh_token': u'pEbXllcSyDPMmFe4X7wmxcvmMU8A_5DfAmISaTSlYvf9cCoO6AlknluOu-2NmfdUfUMunMlrgj3bGMeR0FRctAl3mxJMUbUkJux0zl-fXu4'}
    {u'province': u'Guangdong', u'openid': u'oMaZnwp6MCKAxjBi0anwBsMKf3pw',
     u'headimgurl': u'http://wx.qlogo.cn/mmopen/PiajxSqBRaEJHPI6VNY6HmnSibI23ahh1024IYGEnYtcUxjvHDuqapdXKiacYt0lZWte9dbkVye1RJqXoDx5vI6Pw/0',
     u'language': u'zh_CN', u'city': u'Shenzhen', u'country': u'CN', u'sex': 1,
     u'unionid': u'oh8S_wRSPZ5PfCeFnoDlPV8V1H2M', u'privilege': [], u'nickname': u'\u6728\u5b50\u5a01'}
    """
    unionid = models.CharField('nionid', max_length=50, null=False, blank=False, unique=True)
    openid = models.CharField('openid', max_length=50, null=True, blank=True)
    access_token = models.CharField('access_token', max_length=200, null=True, blank=True)
    refresh_token = models.CharField('refresh_token', max_length=200, null=True, blank=True)
    province = models.CharField(u'省份', max_length=20, null=True, blank=True)
    headimgurl = models.CharField(u'头像图片', max_length=200, null=True, blank=True)
    staticimgurl = models.CharField(u'头像图片', max_length=200, null=True, blank=True, help_text=u'本地图片')
    language = models.CharField(u'语言', max_length=20, null=True, blank=True)
    city = models.CharField(u'城市', max_length=20, null=True, blank=True)
    country = models.CharField(u'国家', max_length=20, null=True, blank=True)
    sex = models.CharField(u'省份', max_length=20, choices=SEX_CHOICES, default='1', null=True, blank=True)
    nickname = models.CharField(u'名称', max_length=20, null=True, blank=True)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(u'修改时间', auto_now=True)

    class Meta:
        managed = False
        db_table = 'core_weixin_customer'

class AliCustomer(models.Model):
    """
    支付宝客户
    {"code":"10000","msg":"Success","avatar":"https:\/\/tfs.alipayobjects.com\/images\/partner\/T1eYdfXnxlXXXXXXXX","city":"深圳市",
    "gender":"m","is_certified":"T","is_student_certified":"F","province":"广东省","user_id":"2088002190090753","user_status":"T","user_type":"2"}
    """
    user_id = models.CharField(u'支付宝唯一ID', max_length=16, null=False, blank=False, unique=True)
    avatar = models.CharField(u'用户头像地址', max_length=400, null=True, blank=True)
    province = models.CharField(u'省份名称', max_length=20, null=True, blank=True)
    city = models.CharField(u'市名称', max_length=20, null=True, blank=True)
    gender = models.CharField(u'性别', max_length=10, null=True, blank=True, help_text=u'性别（F：女性；M：男性）')
    is_certified = models.CharField(u'是否通过实名认证', max_length=1, null=True, blank=True, help_text=u'是否通过实名认证。T是通过 F是没有实名认证。')
    is_student_certified = models.CharField(u'是否是学生', max_length=1, null=True, blank=True, help_text=u'是否是学生。T是 F不是。')
    user_type = models.CharField(u'用户类型', max_length=2, null=True, blank=True, help_text=u'用户类型（1/2） 1代表公司账户2代表个人账户')
    user_status = models.CharField(u'用户状态', max_length=2, null=True, blank=True, help_text=u'用户状态（Q/T/B/W）。 Q代表快速注册用户 T代表已认证用户 B代表被冻结账户 W代表已注册，未激活的账户 ')
    is_admittance = models.CharField(u'芝麻信用准入判断结果', max_length=10, null=True, blank=True, help_text=u'准入判断结果 Y=准入,N=不准入,N/A=无法评估该用户的信用')
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(u'修改时间', auto_now=True)

    class Meta:
        managed = False
        db_table = 'core_ali_customer'

class Manager(models.Model):
    username = models.CharField(max_length=25, null=False, blank=False, unique=True)
    fullname = models.CharField(max_length=50, null=False, blank=False)
    phone = models.CharField(u'电话', max_length=20, null=False, blank=False)
    mobile = models.CharField(u'手机', max_length=20, null=False, blank=False)
    email = models.CharField(u'邮箱', max_length=50, null=False, blank=False)
    im = models.CharField(u'QQ/MSN', max_length=50, null=False, blank=False)

    class Meta:
        managed = False
        db_table = 'core_manager'

#在线申请客户
class ApplyCustomer(models.Model):
    username = models.CharField(max_length=50, null=False, blank=False)
    company = models.CharField(max_length=50, null=False, blank=False)
    linkman = models.CharField(u'联系人', max_length=50, null=True, blank=True)
    ip = models.CharField(u'IP', max_length=20, null=True, blank=True)
    email = models.CharField(u'邮箱', max_length=50, null=True, blank=True)
    qq = models.CharField(u'QQ', max_length=50, null=True, blank=True)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'core_apply_customer'

# #### 客户 #####
class Customer(AbstractBaseUser):
    #id = models.AutoField(primary_key=True, db_column='customer_id', default=0)
    id = models.AutoField(primary_key=True, db_column='customer_id')
    username = models.CharField(max_length=50, null=False, blank=False, unique=True)
    password = models.CharField(max_length=40, null=False, blank=False)
    company = models.CharField(max_length=50, null=False, blank=False)
    linkman = models.CharField(u'联系人', max_length=50, null=True, blank=True)
    phone = models.CharField(u'电话', max_length=20, null=True, blank=True)
    mobile = models.CharField(u'手机', max_length=20, null=True, blank=True)
    email = models.CharField(u'邮箱', max_length=50, null=True, blank=True)
    im = models.CharField(u'QQ/MSN', max_length=50, null=True, blank=True)
    address = models.CharField(u'地址', max_length=120, null=True, blank=True)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, db_column='owner_manager', null=True, blank=True)
    updated = models.DateTimeField(u'更新时间', auto_now=True)
    last_login = models.DateTimeField(u'最后登陆时间', auto_now_add=True)
    last_ip = models.CharField(u'最后登录IP', max_length=20, null=True, blank=True)
    # openid = models.CharField(u'微信OPENID', max_length=50, null=True, blank=True)
    weixin_customer = models.ForeignKey(WeixinCustomer, on_delete=models.SET_NULL, null=True, blank=True)
    ali_customer = models.ForeignKey(AliCustomer, on_delete=models.SET_NULL, related_name='ali_customer', null=True, blank=True)
    homepage = models.CharField(u'网站主页', max_length=200, null=True, blank=True)
    estimate = models.CharField(u'月均发信量', max_length=10, null=False, blank=False)
    industry = models.CharField(u'所属行业', max_length=10, null=False, blank=False)
    web_style = models.CharField(u'页面风格', max_length=1, choices=WEB_STYLE, default='0', null=False, blank=False)
    lang_code = models.CharField(u'用户语言', max_length=10, choices=settings.LANGUAGES, default='zh-hans', null=False, blank=False)
    is_new = models.BooleanField(u'是否是新系统客户', default=False, help_text=u'用于标识, 普通用户从老后台切换到新后台后，需要完善资料。')
    is_register = models.BooleanField(u'支付宝用户', default=False)
    disabled = models.CharField(max_length=1, null=False, blank=False, choices=DISABLED, default='0')
    parent = models.ForeignKey('self', null=True, blank=True, db_index=True,
                               on_delete=models.SET_NULL, related_name='user_children', db_column='parent_id',
                               help_text=u'区别子账户和母账户标记，为空代表子账户，子账户不能再开子账户, 母账户开通子账户后已此作为区别')
    is_remaintain = models.BooleanField(u'是否重新维护客户资料', default=False, help_text=u'默认为Fasle, 不需要重新维护')
    is_bind_ali = models.BooleanField(u'是否绑定支付宝', default=False, help_text=u'是否绑定验证芝麻信用，验证通过后，给客户赠送群发点数，一个客户只能赠送一次')
    new_title = models.CharField(u'新主题', max_length=300, null=True, blank=True,
                                 help_text=u'管理员可修改某个用户在群发平台左上角"U-Mail邮件营销平台"的文字，如果这个文字被修改了，则右下角的二维码部分不显示')
    is_hide_order = models.SmallIntegerField(u'是否隐藏 充值/我的订单/发票管理', default=0, help_text=u'默认为Fasle, 不隐藏')


    USERNAME_FIELD = 'username'
    objects = UserManager()

    def check_password(self, raw_password, t_password=None):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        from passlib.hash import md5_crypt

        return md5_crypt.verify(raw_password, self.password) if not t_password else t_password == self.password

    def get_short_name(self):
        return self.username

    def get_username(self):
        return self.username

    def get_usertype(self):
        return 'customer'

    def __unicode__(self):
        return u'{}({})'.format(self.company, self.username)

    def has_child(self):
        obj = self.user_children.first()
        return True if obj else False

    def service(self):
        services = self.coreCustomer01.all()
        return services[0] if services else None

    def sub_accout_manager(self):
        m = self.sub_account_manager_customer.all()
        o = m[0] if m else None
        o = o if o and o.fullname else None
        return o

    def loginsafe(self):
        logins = self.coreCustomer07.all()
        return logins[0] if logins else None

    def security_token(self):
        tokens = self.settingCustomer02.all()
        return True if tokens else False

    def bind_openid(self, openid):
        self.openid = openid
        self.save()

    def core_invoiceinfo(self):
        obj = self.coreInvoice.first()
        if obj:
            return obj.isvalid
        return False

    def save(self, *args, **kwargs):
        if not self.manager_id:
            self.manager_id = None
        super(Customer, self).save(*args, **kwargs)

    def save_login_log(self, login_ip, ip_info, agent):
        area, title = split_ip_to_area_title(ip_info)
        CoreLog.objects.create(
            user_id=self.pk, user_type='users', target_id=self.pk,
            target_name=u'{0} - {0}'.format(self.username), action='user_login',
            ip=login_ip, desc=u'登录IP：{}<br>登录地区：{}<br>浏览器信息：{}'.format(login_ip, title, agent),
        )
        return

    def save_fast_login_log(self, request, mode='wechat'):
        login_ip = get_client_ip(request)
        ip_search = IpSearch()
        ip_info = ip_search.Find(login_ip)
        area, title = split_ip_to_area_title(ip_info)
        agent = request.META.get('HTTP_USER_AGENT', None)
        if mode == 'wechat':
            CoreLog.objects.create(
                user_id=self.pk, user_type='users', target_id=self.pk,
                target_name=u'{0} - {0}'.format(self.username), action='user_login',
                ip=login_ip, desc=u'登录方式：微信登录<br>登录IP：{}<br>登录地区：{}<br>浏览器信息：{}'.format(login_ip, title, agent),
            )
        elif mode == 'ali':
            CoreLog.objects.create(
                user_id=self.pk, user_type='users', target_id=self.pk,
                target_name=u'{0} - {0}'.format(self.username), action='user_login',
                ip=login_ip, desc=u'登录方式：支付宝快捷登录<br>登录IP：{}<br>登录地区：{}<br>浏览器信息：{}'.format(login_ip, title, agent),
            )
        return

    class Meta:
        managed = False
        db_table = 'core_customer'

class SubAccoutManager(models.Model):
    customer = models.ForeignKey(Customer, related_name='sub_account_manager_customer', db_index=True, null=False, blank=False)
    fullname = models.CharField(max_length=50, null=True, blank=True)
    mobile = models.CharField(u'手机', max_length=20, null=True, blank=True)
    im = models.CharField(u'QQ/MSN', max_length=50, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'sub_account_manager'

# #### 客户与内容偏向 关联关系表 #####
class CustomerContentRel(models.Model):
    customer = models.ForeignKey(Customer, related_name='customer_content_rel', db_index=True, null=False, blank=False)
    content_type = models.CharField(u'内容偏向', max_length=10, null=False, blank=False)

    class Meta:
        managed = False
        db_table = 'core_customer_content_rel'

# #### 客户与获知渠道 关联关系表 #####
class CustomerWayRel(models.Model):
    customer = models.ForeignKey(Customer, related_name='customer_way_rel', db_index=True, null=False, blank=False)
    way_type = models.CharField(u'获知渠道', max_length=10, null=False, blank=False)

    class Meta:
        managed = False
        db_table = 'core_customer_way_rel'

STORE_TYPE = (
    ('1', u'新建'),
    ('2', u'追加')
)
IMPORT_LOG_ADDR_TYPE = (
    ('tag', u'标签地址库'),
    ('active', u'活跃地址库')
)

class CustomerImportLog(models.Model):
    '''
    客服赠送地址给客服日志
    '''
    customer = models.ForeignKey(Customer, related_name='customer_import_log', db_index=True, null=False, blank=False)
    store_count = models.IntegerField(u"入库数量", default=0)
    addr_type = models.CharField(u'地址来源', max_length=10, null=False, blank=False, choices=IMPORT_LOG_ADDR_TYPE, default='tag')
    store_type = models.CharField(u'入库方式', max_length=5, null=False, blank=False, choices=STORE_TYPE, default='1')
    maillist_name = models.CharField(u'地址池名称', max_length=50, null=True, blank=True, help_text=u'新建地址池名称')
    maillist_id = models.IntegerField(u"地址池ID", default=0, help_text=u'追加地址池ID', db_index=True)
    store_status = models.BooleanField(u'导入状态', default=False, help_text=u'True表示正在入库。')
    json_text = models.TextField(u'json记录')
    store_real = models.IntegerField(u"实际入库数量", default=0)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(u'修改时间', null=True, auto_now=True)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, related_name='customerlog_manager', db_index=True, null=True, blank=True)
    description = models.CharField(u'管理员备注', max_length=500, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'core_customer_import_log'

# #### 客户服务 #####
class Services(models.Model):
    customer = models.ForeignKey(Customer, related_name='coreCustomer01', db_index=True, null=False, blank=False,
                                 db_column='customer_id')
    is_trial = models.CharField(u'是否为测试用户', max_length=1, null=False, blank=False, choices=CHOICE_0_1, default='0')
    is_verify = models.CharField(u'是否为审核用户', max_length=1, null=False, blank=False, choices=CHOICE_0_1, default='0')
    server_type = models.CharField(max_length=1, null=False, blank=False, choices=SERVER_TYPE, default='0')
    send_type = models.CharField(max_length=16, null=False, blank=False, choices=SEND_TYPE, default='local')
    service_type = models.CharField(max_length=16, null=False, blank=False, choices=SERVICE_TYPE, default='all')
    service_start = models.DateTimeField(u'服务开始时间', auto_now_add=True)
    service_end = models.DateTimeField(u'服务结束时间', null=False, default='0000-00-00 00:00:00')
    qty_count = models.IntegerField(u'剩余群发量', default=0)
    qty_valid = models.IntegerField(u'剩余群发量',default=0)
    qty_buytotal = models.IntegerField(u'总购买的群发量', default=0)
    error_stat_ratio = models.FloatField(null=False, blank=False, default=0.15)
    refuse_error_stat_ratio = models.FloatField(null=False, blank=False, default=0.50)
    ws_rate_limit = models.IntegerField(default=0)
    module_permit = models.TextField(null=True, blank=True)
    disabled = models.CharField(max_length=1, null=False, blank=False, choices=DISABLED, default='0')
    disabled_date = ZeroDateTimeField()
    track_domain = models.CharField(u'客户指定域名', max_length=100, null=True, blank=True, help_text=u'客户指定域名，替换跟踪统计链接域名')
    addr_export = models.CharField(u'开启导出按钮', max_length=1, null=False, blank=False, choices=CHOICE_0_1, default='0',
                                   help_text=u'地址池导出功能，1为开启，0为禁用，默认为1')
    addr_export_max = models.IntegerField(u'地址池导出限制', default=0, help_text=u'地址导出最大数，0为无限制')
    timezone = models.SmallIntegerField(u'时区', default=8, help_text=u'时区，相对GMT时间，如8表示GMT+8，北京时间')
    cannotview_html = models.TextField(null=True, blank=True, help_text=u'邮件无法正常显示，提示查看在线版本的内容')
    unsubscribe_html = models.TextField(null=True, blank=True, help_text=u'退订邮件列表链接内容')
    is_maintain = models.SmallIntegerField(default=0)
    is_high_quality = models.SmallIntegerField(default=0)
    is_replace_sender = models.SmallIntegerField(default=0)
    is_allow_red_tpl = models.SmallIntegerField(default=1)
    is_allow_cy_tpl = models.SmallIntegerField(default=0)
    maintain_rate = models.IntegerField(default=50)
    updated = models.DateTimeField(u'更新时间', auto_now=True)
    is_autoremove = models.BooleanField(u'无效地址自动删除开关', default=1,
                                        help_text=u'选中即为开启，默认不开启，开启表示 邮件发送后自动将无效地址从地址池中移除。')
    is_auto_duplicate = models.BooleanField(u'联系人分类之间去重开关', default=0,
                                            help_text=u'选中即为开启，默认不开启，开启表示 系统自动去重各联系人分类之间的地址，即一个邮件地址在所有联系人分类中唯一存在。')
    duplicate_type = models.CharField(u'联系人分类之间去重方式', max_length=10, null=False, blank=False, choices=DUPLICATE_TYPE, default='old')
    is_stmp = models.BooleanField(u'支持SMTP密码修改', default=0)
    is_need_receipt = models.BooleanField(u'邮件阅读回执', default=0)
    is_open_accurate = models.BooleanField(u'开启精准邮件数据服务', default=False, help_text=u'管理员指定对某些用户开放“精准邮件数据服务”')
    is_umail = models.BooleanField(u'是否是U-Mail账户', default=False, help_text=u'用于区别一般账户。')

    is_share_flag = models.CharField(u'共享标志', max_length=10, null=False, blank=False, choices=IS_SHEAR_FLAG, default='1',
                                     help_text=u'1.母账户 2.不共享（分配） 3.部分共享 4.全部共享')
    limit_qty = models.IntegerField(u'限制共享数量',default=0, help_text=u'is_share_limit为False时的限制共享数量。')
    is_address = models.BooleanField(u'子账户查看地址池权限', default=True)
    is_template = models.BooleanField(u'子账户查看模板权限', default=True)
    is_task = models.BooleanField(u'子账户查看任务权限', default=True)
    is_pushcrew = models.BooleanField(u'设置为关注用户', default=False)
    is_track_export = models.BooleanField(u"设置用户导出跟踪统计地址权限", default=True, help_text=u"主要针对某些账户的子账户")

    class Meta:
        managed = False
        db_table = 'core_services'

    def __unicode__(self):
        return u'Service({})'.format(self.customer)


##### 插入系统链接的配置(键值对) #####
class Prefs(models.Model):
    name = models.CharField(u'键', max_length=30, null=False, blank=False, db_index=True)
    value = models.TextField(u'值', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'core_prefs'

##### 客户高级设置(操作模板时更新) #####
class CustomerTplSetting(models.Model):
    customer = models.ForeignKey(Customer, related_name='coreCustomer02', db_index=True, null=False, blank=False,
                                 db_column='customer_id')
    encoding = models.CharField(u'邮件编码', max_length=50, null=False, blank=False, choices=ENCODING_TYPE,
                                default='base64')
    character = models.CharField(u'转换字符集', max_length=32, null=False, blank=False, choices=CHARACTER_TYPE,
                                 default='utf-8')
    image_encode = models.CharField(u'是否内嵌照片', max_length=32, null=False, blank=False, choices=IMAGE_TYPE, default='N',
                                    help_text=u'否：邮件内的图片会自动上传到U-Mail服务器上，以外部图像链接的方式显示图片。'
                                              '是：邮件所使用的图像内嵌在邮件消息中。 这将导致邮件大小的增加(扣除更多群发点数), 但是邮件却可以脱机浏览。 ')
    attachtype = models.CharField(u'附件设置', max_length=32, null=False, blank=False, choices=ATTACH_TYPE,
                                  default=u'common',
                                  help_text=u'传统附件：以普通的邮件附件形式发送，附件大小会增加邮件大小，但是附件可以脱机查看。'
                                            u'在线附件：邮件的附件以HTML超链接的形式内嵌在邮件消息中，不会增大邮件大小，但是需要网络才可访问。 ')

    class Meta:
        managed = False
        db_table = 'core_customer_tpl_setting'


class MailBox(models.Model):
    customer = models.ForeignKey(Customer, related_name='coreCustomer04', db_index=True, null=False, blank=False,
                                 db_column='customer_id')
    domain = models.CharField(u'客户域名', max_length=50, db_index=True, null=True, blank=True)
    name = models.CharField(u'发件人名称', max_length=25, null=True, blank=True)
    mailbox = models.CharField(u'发件人邮箱', max_length=80, db_index=True, null=True, blank=True)
    password = models.CharField(u'密码', max_length=40, null=True, blank=True)
    disabled = models.CharField(u'状态', max_length=1, null=False, blank=False, choices=DISABLED, default='0')

    def __unicode__(self):
        return self.mailbox

    class Meta:
        managed = False
        db_table = 'core_mailbox'

class CommonType(models.Model):
    " 变量分类 "
    var_type = models.CharField(u'变量类型', max_length=10, unique=True, null=False, blank=False,
                                help_text=u'只能是英文字母，前后不能包含空格，如：joke 。')
    name = models.CharField(u'变量名称', max_length=10, unique=True, null=False, blank=False,
                            help_text=u'和类变量型对应，如：笑话库 对应 joke。')
    dict_type = models.CharField(u'变量类型键', max_length=20, null=False, blank=False)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    disabled = models.BooleanField(u'是否禁用', default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'core_common_type'


class CoreLog(models.Model):
    " 操作日志列表 "
    datetime = models.DateTimeField(u'操作时间', auto_now_add=True)
    user = models.ForeignKey(Customer, related_name='coreCustomer05', null=False, blank=False, db_column='user_id') # 操作人员
    user_type = models.CharField(u'用户类型', max_length=20, null=False, blank=False, choices=USER_TYPE, default='manager')
    target = models.ForeignKey(Customer, related_name='coreCustomer06', null=False, blank=False, db_column='target_id') # 被操作对象
    target_name = models.CharField(u'名称', max_length=80, null=True, blank=True)
    action = models.CharField(u'操作类型', max_length=20, null=False, blank=False, choices=ACTION_TYPE, default='', db_index=True)
    desc = models.TextField(u'说明')
    ip = models.CharField(u'名称', max_length=15, null=True, blank=True)

    def __unicode__(self):
        return self.target_name

    class Meta:
        managed = False
        db_table = 'core_log'

class CoreLogAutoReturn(models.Model):
    """系统自动返点详细日志"""
    datetime = models.DateTimeField(u'操作时间', auto_now_add=True)
    customer = models.ForeignKey(Customer, null=False, blank=False)
    task_ident = models.CharField(u'任务名称', max_length=50, null=True, blank=True)
    rebate = models.IntegerField(u'返点数', default=0)

    class Meta:
        managed = False
        db_table = 'core_log_auto_return'

class CoreArea(models.Model):
    ''' 客户区域 '''
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children',
                               db_column='pid')
    name = models.CharField(u'区域名称', max_length=50, null=False, blank=False)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'core_customer_area'


class CoreLoginAreaIp(models.Model):
    " 客户登陆安全设置 "
    user = models.ForeignKey(Customer, related_name='coreCustomer07', null=False, blank=False, db_column='user_id')
    is_open = models.BooleanField(u'是否开启登陆保护', default=False)
    area = models.TextField(u'客户登陆所属区域', help_text=u'区域之间用“,”号隔开')
    ip = models.TextField(u'客户登陆所属IP', help_text=u'IP之间用“,”号隔开')

    def __unicode__(self):
        if self.area and self.ip:
            return u'{}--{}'.format(self.area, self.ip)
        if self.area:
            return self.area
        if self.ip:
            return self.ip

    class Meta:
        managed = False
        db_table = 'core_customer_area_ip_setting'


class CoreSuggest(models.Model):
    " 客户建议 "
    customer = models.ForeignKey(Customer, related_name='coreCustomer08', null=False, blank=False,
                                 db_column='customer_id')
    score = models.SmallIntegerField(u'评价级别', default=1)
    suggest = models.CharField(u'建议', max_length=255, null=True, blank=True)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'core_suggest'


class CorePasswordAlter(models.Model):
    " 密码修改 "
    customer = models.ForeignKey(Customer, related_name='coreCustomer09', null=False, blank=False,
                                 db_column='customer_id')
    uuid = models.CharField('UUID', max_length=50, null=False, blank=False)
    token = models.CharField('TOKEN', max_length=50, null=False, blank=False)
    isvalid = models.BooleanField(u'是否实现', default=True)
    expire_time = models.FloatField(u'过期时间', default=0)

    def __unicode__(self):
        return self.customer.username

    class Meta:
        managed = False
        unique_together = (("uuid", "token"),)
        db_table = 'core_password_alter'


class CustomerDomain(models.Model):
    """
    客户发送域名
    """
    customer = models.ForeignKey(Customer, related_name='customer_domain')
    # customer_id = models.IntegerField(u'客户ID')
    domain = models.CharField(u'发送域名', max_length=100, null=False, blank=False,
                              help_text=u'不建议添加企业邮箱域名，将导致企业邮箱收信异常，建议在已有企业邮箱域名的情况下创建二级域名。')
    status = models.CharField(u'状态', max_length=1, default='N', choices=CUSTOMER_DOMAIN_STATUS)
    dkim_selector = models.CharField(u'子域名', default='umail', max_length=50, null=True, blank=True)
    dkim_private = models.TextField(u'私钥', null=True, blank=True)
    dkim_public = models.TextField(u'公钥', null=True, blank=True)
    add_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    is_spf = models.CharField(u'spf检测状态', max_length=1, default='N', choices=CUSTOMER_DOMAIN_STATUS)
    is_mx = models.CharField(u'mx检测状态', max_length=1, default='N', choices=CUSTOMER_DOMAIN_STATUS)
    is_dkim = models.CharField(u'dkim检测状态', max_length=1, default='N', choices=CUSTOMER_DOMAIN_STATUS)
    is_register = models.BooleanField(u'是否用于自主注册', default=False, help_text=u'系统域名是否用于自主注册，True:使用')

    def save(self, *args, **kwargs):
        if self.status == 'Y':
            CustomerMailbox.objects.filter(customer=self.customer, domain=self.domain).update(disabled='0')
        else:
            CustomerMailbox.objects.filter(customer=self.customer, domain=self.domain).update(disabled='1')
        super(CustomerDomain, self).save(*args, **kwargs)


    def api_sync(self, op):
        """
        op: add-domain, del-domain, del-domain-by-cid
        """
        url = '{host}?action={op}&cid={cid}&domain={domain}&auth={auth}'.format(**{
            'host': settings.RECEIPT_URL,
            'op': op,
            'cid': self.customer.id,
            'domain': self.domain,
            'auth': self.gen_key()
        })
        urllib2.urlopen(url)

    def gen_key(self):
        return hashlib.md5('%s-%s' % (settings.RECEIPT_AUTH_KEY, datetime.datetime.now().strftime("%Y%m%d"))).hexdigest()

    def get_secondary_domain(self):
        return domainparse.parse_domain(self.domain, action='secondary')

    def get_main_domain(self):
        return domainparse.parse_domain(self.domain, action='main')

    class Meta:
        managed = False
        db_table = 'core_domain'


class CustomerMailbox(models.Model):
    """
    客户发送账号
    """
    customer = models.ForeignKey(Customer, related_name='customer_mailbox')
    domain = models.CharField(u'发送域名', max_length=100, null=False, blank=False)
    name = models.CharField(u'名称', max_length=30, null=True, blank=True)
    mailbox = models.CharField(u'邮箱账号', max_length=80, null=True, blank=True)
    password = models.CharField(u'密码', max_length=40, null=True, blank=True)
    disabled = models.CharField(u'是否禁用', choices=DISABLED, default='0', max_length=1, null=True, blank=True)
    limit_qty = models.IntegerField(u'自主注册限制封数', default=0)

    def api_sync(self, op):
        """
        op: add-mailbox, set-mailbox-pass, del-mailbox
        """
        url = '{host}?action={op}&cid={cid}&email={email}&pass={pass}&auth={auth}'.format(**{
            'host': settings.RECEIPT_URL,
            'op': op,
            'cid': self.customer.id,
            'email': self.mailbox,
            'pass': urllib.quote_plus(self.password),
            'auth': self.gen_key()
        })
        urllib2.urlopen(url)

    def gen_key(self):
        return hashlib.md5('%s-%s' % (settings.RECEIPT_AUTH_KEY, datetime.datetime.now().strftime("%Y%m%d"))).hexdigest()

    class Meta:
        managed = False
        db_table = 'core_mailbox'

class CustomerDomainMailboxRelManager(models.Manager):

    def get_content_type(self, type):
        if type == u'domain':
            ctype, _ = ContentType.objects.get_or_create(app_label='core', model='customerdomain')
        if type == u'mailbox':
            ctype, _ = ContentType.objects.get_or_create(app_label='core', model='customermailbox')
        return ctype

class CustomerDomainMailboxRel(models.Model):
    customer = models.ForeignKey(Customer, related_name='customer_domain_rel', null=False, blank=False, db_index=True) # 子账户的ID
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False, blank=False, db_index=True)
    object_id = models.PositiveIntegerField('object_id', null=False, blank=False, db_index=True) # 子账户关联的父ID的发件人ID或者域名ID
    object = GenericForeignKey('content_type', 'object_id')

    objects = CustomerDomainMailboxRelManager()

    class Meta:
        unique_together = (('customer', 'content_type', 'object_id'),)
        managed = False
        db_table = 'core_domain_rel'

class DefaultMailbox(models.Model):
    account = models.CharField(u'名称', max_length=64, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'core_mss_default_acct'


"""
class Domain(models.Model):
    customer = models.ForeignKey(Customer, related_name='domain')
    domain = models.CharField(u'发送域名', max_length=100, null=False, blank=False)
    grant_agent = models.CharField(u'代理商', max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'core_domain'
"""

class Invoice(models.Model):
    """ 客户发票收取信息 """
    customer = models.ForeignKey(Customer, related_name='coreInvoice', db_index=True)
    # 物流信息
    recipient = models.CharField(u'收件人姓名', null=True, blank=True, max_length=50)
    address = models.CharField(u'发票寄送地址', null=True, blank=True, max_length=200)
    phone = models.CharField(u'联系方式', null=True, blank=True, max_length=20, help_text=u'手机或固定电话（加区号）')
    zipcode = models.CharField(u'邮政编码', null=True, blank=True, max_length=20)
    # 发票抬头（普通）、纳税人名称（专）
    invoice_type = models.CharField(u'发票类型', choices=INVOICE_TYPE, max_length=10, default='1')
    invoice_title = models.CharField(u'发票抬头', null=True, blank=True, max_length=100)
    # 专用发票
    tax_number = models.CharField(u'纳税人识别号', null=True, blank=True, max_length=50, help_text=u'税务登记证编号')
    bank = models.CharField(u'开户银行', null=True, blank=True, max_length=100, help_text=u'银行名称+开户省市区+支行名称')
    acc_number = models.CharField(u'银行账号', null=True, blank=True, max_length=50)
    company_addr = models.CharField(u'企业注册地址', null=True, blank=True, max_length=200)
    company_phone = models.CharField(u'企业注册电话', null=True, blank=True, max_length=20)
    # 一般纳税人资格认证复印件
    file_type = models.CharField(u'文件类型', max_length=100, null=True, blank=True)
    file_path = models.CharField(u'文件路径', max_length=100, null=True, blank=True)
    isvalid = models.BooleanField(u'是否有效', default=False)

    class Meta:
        managed = False
        db_table = 'core_invoice'

class CustomerInvoice(models.Model):
    """ 客户发票 """
    customer = models.ForeignKey(Customer, related_name='invoice', db_index=True)
    amount = models.DecimalField(verbose_name=u'发票金额', max_digits=9, decimal_places=0)
    description = models.TextField(u'备注', help_text=u'填写快递单号等信息，便于客户查询')
    status = models.CharField(u'发票状态', choices=INVOICE_STATUS, max_length=10, default='apply')
    created = models.DateTimeField(verbose_name=u'索取时间', auto_now_add=True)
    invoice_type = models.CharField(u'发票类型', choices=INVOICE_TYPE, max_length=10, default='1')
    invoice_no = models.CharField(u'发票编号', null=False, blank=False, max_length=100, default='-')
    invoice_title = models.CharField(u'发票抬头', null=False, blank=False, max_length=100)
    recipient = models.CharField(u'收件人', null=False, blank=False, max_length=50)
    address = models.CharField(u'收取地址', null=False, blank=False, max_length=200)
    phone = models.CharField(u'联系电话', null=False, blank=False, max_length=20)
    track_no = models.CharField(u'快递单号', null=False, blank=False, max_length=100, default='-')
    zipcode = models.CharField(u'邮政编码', null=True, blank=True, max_length=20)
    # 专用发票
    tax_number = models.CharField(u'纳税人识别号', null=True, blank=True, max_length=50, help_text=u'税务登记证编号')
    bank = models.CharField(u'开户银行', null=True, blank=True, max_length=100, help_text=u'银行名称+开户省市区+支行名称')
    acc_number = models.CharField(u'银行账号', null=True, blank=True, max_length=50)
    company_addr = models.CharField(u'企业注册地址', null=True, blank=True, max_length=200)
    company_phone = models.CharField(u'企业注册电话', null=True, blank=True, max_length=20)

    class Meta:
        managed = False
        db_table = 'core_customer_invoice'

    def order(self):
        return self.invoice.all()

class CustomerOrder(models.Model):
    """
    客户订单
    """
    orderno = models.CharField(verbose_name=u'订单号', max_length=50, unique=True, editable=False)
    customer = models.ForeignKey(Customer, related_name='order', db_index=True)
    invoice = models.ForeignKey(CustomerInvoice, related_name='invoice', null=True, blank=True)
    product_desc = models.CharField(verbose_name=u'商品描述', max_length=128, null=False, blank=False)
    product_detail = models.TextField(verbose_name=u'商品详情', max_length=1000, null=False, blank=False)
    fee = models.DecimalField(verbose_name=u'金额(单位:元)', max_digits=6, decimal_places=0, null=False, blank=False)
    qty_buy = models.IntegerField(u'购买点数', default=0)
    attach = models.CharField(verbose_name=u'附加数据', max_length=127, null=True, blank=True)
    dt_start = models.DateTimeField(verbose_name=u'交易开始时间', null=True, blank=True)
    dt_end = models.DateTimeField(verbose_name=u'交易失效时间', null=True, blank=True)
    dt_pay = models.DateTimeField(verbose_name=u'付款时间', null=True, blank=True)
    status = models.CharField(u'状态', choices=ORDER_STATUS, max_length=10, default='waiting')
    payway = models.CharField(verbose_name=u'支付方式', max_length=10, null=False, blank=False, choices=PAY_WAY,
                              default=PAY_WAY[0][0])
    transaction_id = models.CharField(u'微信/支付宝订单号', max_length=40, null=True, blank=True)
    bank_type = models.CharField(u'微信订单号', max_length=16, null=True, blank=True)
    openid = models.CharField(u'微信付款人openid或支付宝buyer_id', max_length=50, null=True, blank=True, help_text=u'对与公众号的')
    buyer = models.CharField(u'付款人名称', max_length=50, null=True, blank=True)
    is_subscribe = models.BooleanField(u'是否订阅公众号', default=False)
    return_code = models.CharField(u'微信返回状态码', max_length=16, null=True, blank=True,
                                   help_text=u'SUCCESS/FAIL 此字段是通信标识，非交易标识，交易是否成功需要查看result_code来判断')
    return_msg = models.CharField(u'微信返回信息', max_length=128, null=True, blank=True,
                                  help_text=u"返回信息，如非空，为错误原因 签名失败  参数格式校验错误")
    result_code = models.CharField(u'业务结果', max_length=20, null=True, blank=True, help_text=u'SUCCESS/FAIL')
    created = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(verbose_name=u'修改时间', auto_now=True)

    class Meta:
        managed = False
        db_table = 'core_customer_order'

    @property
    def pre_pay_url(self):
        url = reverse('ali_pre_pay') if self.payway == 'alipay' else reverse('wx_pre_pay')
        return '{}?id={}'.format(url, self.orderno)

    def save(self, *args, **kwargs):
        if not self.orderno:
            self.orderno = time.strftime('%Y%m%d%H%M%S') + get_random_string(18).upper()
        super(CustomerOrder, self).save(*args, **kwargs)


class Pricing(models.Model):
    """
    群发套餐设置
    """
    name = models.CharField(u'套餐名称', max_length=100, null=False, blank=False, help_text=u'如：体验版套餐, 标准套餐...')
    pricing = models.IntegerField(u'套餐定价金额', null=False, blank=False, help_text=u'套餐定价金额，单位：人民币￥(元）, 只能为整数')
    buy_count = models.IntegerField(u'充值点数', null=False, blank=False, help_text=u'套餐对应的群发充值点数')
    desp = models.TextField(u'套餐描述', help_text=u'换行显示')
    is_popular = models.BooleanField(u'是否为推荐套餐', default=False)
    disabled = models.BooleanField(u'是否禁用', default=False)
    created = models.DateTimeField(u'添加日期', auto_now_add=True)
    updated = models.DateTimeField(u'修改日期', auto_now=True)

    class Meta:
        managed = False
        db_table = 'core_pricing'

    def desp_as_list(self):
        return self.desp.replace('\r', '').split('\n')

class CoreNotice(models.Model):
    ''' 站内公告 '''
    title = models.CharField(u'标题', max_length=255, null=False, blank=False)
    content = models.TextField(u'站内通知内容', null=False, blank=False)
    created = models.DateTimeField(u'创建时间', null=False, blank=False, auto_now_add=True)
    start_time = models.DateTimeField(u'生效时间', null=False, blank=False)
    validity = models.IntegerField(u'有效期', null=False, blank=False, default=0, help_text=u'单位：天， 0代表永久有效期。')

    def __unicode__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'core_notice'

class CoreNoticeLog(models.Model):
    ''' 客户阅读公告日志 '''
    customer = models.ForeignKey(Customer, related_name='noticelog01', db_index=True, null=False, blank=False)
    notice = models.ForeignKey(CoreNotice, related_name='noticelog02', db_index=True, null=False, blank=False)
    is_read = models.BooleanField(u'是否已阅读', default=False, help_text=u'0为未读，1为已读')
    is_del = models.BooleanField(u'是否删除', default=False, help_text=u'0为未删除，1为已删除')
    read_time = models.DateTimeField(u'查看阅读时间', null=True, blank=True)
    del_time = models.DateTimeField(u'删除时间', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'core_notice_log'



class CoreNotification(models.Model):
    '''
    客户通知
    '''
    subject = models.CharField(u'通知主题', max_length=50, null=True)
    content = models.TextField(u'通知内容')
    type = models.CharField(u'通知类型', max_length=5, choices=NOTIFICATION_TYPE)
    customer = models.ForeignKey(Customer, related_name='corenotify01', db_index=True, null=False, blank=False)
    is_read = models.BooleanField(u'是否阅读', default=False, help_text=u'通知是否阅读')
    is_notice = models.BooleanField(u'是否发站内通知', default=False)
    is_sms = models.BooleanField(u'是否发短信通知', default=False)
    is_email = models.BooleanField(u'是否发邮件通知', default=False)
    created = models.DateTimeField(u'创建日期', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'core_notification'

class CoreNoticeTemplate(models.Model):
    remote_login = models.TextField(u'异地登录模板', null=True, blank=True, help_text=u'邮件和短信一个模板，短信去html代码。'
                                                                                u'{COMPANY}代表公司，{NAME}代表姓名， {TIME}代表操作时间；\n'
                                                                                u'——异地登录模板：      {AREA}代表异地登录地区；\n'
                                                                                u'——充值成功模板：      {POINT}代表充值点数；\n'
                                                                                u'——域名解析异常模板：  {DOMAIN}代表异常域名；\n'
                                                                                u'——邮件审核不通过模板：{TASK}代表审核不通过的任务名称；\n'
                                                                                u'——余额到达警戒值模板：{LAVE}代表群发量余额。\n')
    success_recharge = models.TextField(u'充值成功模板', null=True, blank=True)
    odd_domain = models.TextField(u'域名解析异常模板', null=True, blank=True)
    odd_consume = models.TextField(u'邮件审核不通过模板', null=True, blank=True)
    reduce_credit = models.TextField(u'余额到达警戒值模板', null=True, blank=True)
    alter_contacts = models.TextField(u'联系人信息修改模板', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'core_notice_template'


SMTP_DEFAULT = [
    ('Y', u'是'),
    ('N', u'否'),]

class CoreMssSmtpAcct(models.Model):
    server = models.CharField(u'服务器', max_length=64, null=True, blank=True)
    port = models.IntegerField(u'端口', default=25)
    account = models.CharField(u'账号', max_length=64, null=True, blank=True)
    password = models.CharField(u'密码', max_length=64, null=True, blank=True)
    domain = models.TextField(u'域名', null=True, blank=True)
    default = models.CharField(u'默认服务器', max_length=1, choices=SMTP_DEFAULT, null=False, blank=False, default='N')

    class Meta:
        managed = False
        db_table = 'core_mss_smtp_acct'

class CoreUrlRemark(models.Model):
    url = models.CharField(u'URL', max_length=200, null=False, blank=False, unique=True, help_text=u'url地址')
    remark = models.TextField(u'备注', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'core_url_remark'

class CustomerTrackDomain(models.Model):
    '''
    跟踪域名管理
    '''
    customer = models.ForeignKey(Customer, related_name='trackdomain', db_index=True, null=False, blank=False)
    domain = models.CharField(u'跟踪统计链接域名', max_length=100, null=False, blank=False, help_text=u'请将该域名的CNAME域名记录指向count1.bestedm.org')
    isdefault = models.BooleanField('默认域名', default=False)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'core_track_domain'

class CoreVerifyAli(models.Model):
    '''
    支付宝注册 短信验证码记录
    1. 限制当天支付宝次数
    2. 限制手机次数
    '''
    user_id = models.CharField(u'支付宝唯一ID', max_length=16, null=False, blank=False, unique=True)
    user_count = models.IntegerField(u'获取次数', default=0, help_text=u'限制当天支付宝获取次数')
    phone = models.CharField(u'手机', max_length=20, null=False, blank=False)
    code = models.CharField(u'验证码', max_length=10, null=False, blank=False)
    expire_time = models.IntegerField(u'过期时间', default=0)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(u'修改时间', auto_now=True)

    def __unicode__(self):
        return self.user_id

    class Meta:
        managed = False
        db_table = 'core_verify_ali'


class CheckSetting(models.Model):
    """
    群发系统垃圾检测设置
    SMTP账号发送检测就是用一个或多个smtp账号发送测试，如果返回信息里有垃圾邮件标志，则模板为红色
    检测垃圾的SMTP账号可能会有多个，管理员后台设置格式范例：
    QQ反垃圾检测引擎 smtp.qq.com 56656565@qq.com password 收件人邮箱
    某某反垃圾引擎 smtp.aaa.com  adfb@ss.com password 收件人邮箱
    系统调用上述SMTP账号投递邮件，如果出现 垃圾邮件标志，则返回红色并提示 某某反垃圾引擎 检测为垃圾邮件
    """
    name = models.CharField(u'名称', max_length=50, null=False, blank=False, help_text=u'发垃圾检测引擎名称，如：QQ反垃圾检测引擎, 某某反垃圾检测引擎...')
    smtp_server = models.CharField(u'SMTP服务商', max_length=100, null=False, blank=False, help_text=u'SMTP服务商地址, 如：smtp.qq.com')
    smtp_port = models.IntegerField(u'SMTP端口', default=25, help_text=u'SMTP服务商端口')
    account = models.CharField(u'SMTP账号', max_length=100, null=False, blank=False, help_text=u'SMTP账号')
    password = models.CharField(u'SMTP密码', max_length=100, null=False, blank=False, help_text=u'SMTP密码')
    receiver = models.CharField(u'收件人邮箱', max_length=100, null=False, blank=False, help_text=u"""
        SMTP账号发送检测就是用一个或多个smtp账号发送测试，如果返回信息里有垃圾邮件标志，则模板为红色
        检测垃圾的SMTP账号可能会有多个，管理员后台设置格式范例：
        QQ反垃圾检测引擎 smtp.qq.com 56656565@qq.com password 收件人邮箱
        某某反垃圾引擎 smtp.aaa.com  adfb@ss.com password 收件人邮箱
        系统调用上述SMTP账号投递邮件，如果出现 垃圾邮件标志，则返回红色并提示 某某反垃圾引擎 检测为垃圾邮件
    """)
    tip = models.TextField(u'信息提示', help_text=u'当此项SMTP账号检测命中时，整行文字显示此内容。')

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'core_check_setting'


##### 浏览器最低版本设置 #####
class CoreBrowserConfig(models.Model):
    name_en = models.CharField(u'浏览器英文名称', max_length=50, null=False, blank=False, unique=True)
    version = models.IntegerField(u'浏览器最低版本', null=False, blank=False)
    name_zh = models.CharField(u'浏览器中文名称', max_length=50, null=True, blank=True)
    rule = models.CharField(u'匹配规则', max_length=200, null=False, blank=False)

    class Meta:
        managed = False
        db_table = 'core_browser_config'

class SysPicDomain(models.Model):
    """
    图片域名设置， 新增、禁用、启用
    """
    domain = models.CharField(u'域名', null=False, blank=False, unique=True, max_length=100, help_text=u'域名只能以http://开头，不支持正则，域名请填小写（系统自动转小写）,比如：http://www.example.com')
    isvalid = models.BooleanField(u'是否启用', default=True)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(u'修改时间', null=True, auto_now=True)

    def __unicode__(self):
        return self.domain

    class Meta:
        managed = False
        db_table = 'core_pic_domain'

class MailAccurateService(models.Model):
    """
    精准邮件数据服务
    """
    customer = models.ForeignKey(Customer, related_name='mailAccurateService', db_index=True, null=False, blank=False)
    json_text = models.TextField(u'json记录', null=True, blank=True, help_text=u'')
    remark = models.TextField(u'其他说明', null=True, blank=True)
    linkman = models.CharField(u'联系人', max_length=50, null=False, blank=False)
    mobile = models.CharField(u'手机', max_length=20, null=False, blank=False)
    is_email = models.BooleanField(u'是否已发送邮件', default=False, help_text=u'发送邮件通知业务人员')
    created = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'core_accurate_service'

    def get_email_subject(self):
        return u'精准邮件数据申请（{}）'.format(self.customer.company)

    def get_email_content(self):
        content = u"""
        <p>客户申请的详细资料如下：</p>
        <p style="margin-left:13px;"> <strong>公司名称：</strong>{}</p>
        <p style="margin-left:13px;"> <strong>申请时间：</strong>{}</p>
        <p style="margin-left:13px;"> <strong>联系人：</strong>{}</p>
        <p style="margin-left:13px;"> <strong>手机号码：</strong>{}</p>
        <div style="clear:both;height:13px;"></div>
        {}
        <p style="margin-left:13px;"> <strong>其他说明：</strong>{}</p>
        """.format(
            self.customer.company,
            date_format(self.created, "Y-m-d H:i:s"),
            self.linkman,
            self.mobile,
            self.show_json_text_html(),
            self.remark
        )
        return content

    def show_json_text_html(self):
        json_vals = json.loads(self.json_text)
        namelist = json_vals['namelist']
        html = ''
        if namelist:
            tag_category_vals = {}
            tag_objs = Tag.objects.filter(id__in=namelist)
            for tag_obj in tag_objs:
                category_id = int(tag_obj.category_id)
                tag_name = u'{} > {}'.format(tag_obj.parent.name, tag_obj.name) if tag_obj.parent else tag_obj.name
                if category_id in tag_category_vals:
                    tag_category_vals[category_id]['tag_name'].append(tag_name)
                else:
                    tag_category_vals.update({
                        category_id: {
                            'cat_name': tag_obj.category.name,
                            'tag_name': [tag_name],
                        }
                    })
            for v in tag_category_vals.values():
                html += u'<p style="margin-left:13px;"><strong style="margin-right: 5px;">{}：</strong>'.format(v['cat_name'])
                for tag_name in v['tag_name']:
                    html += u'''<span style="display:inline-block;min-width:10px;padding:3px 7px;font-size:12px;font-weight:700;color:#fff;line-height:1;vertical-align:middle;vertical-align:baseline;white-space: nowrap;text-align:center;background-color:#999;border-radius:10px;background:#3276B1!important">
                    {}</span>'''.format(tag_name)
                html += '</p>'
            return html
        return html

class TestChannel(models.Model):
    """
    测试通道地址
    """
    email = models.CharField(u'邮箱', max_length=100, db_index=True, unique=True)
    customer = models.ForeignKey(Customer, related_name='test_channle_customer', null=True, blank=True)
    manager = models.ForeignKey(Manager, null=True, blank=True, related_name='test_channle_manager')
    hits = models.IntegerField(default=0)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    is_quick_send = models.BooleanField(u'是否来自快速发送', default=False)

    class Meta:
        managed = False
        db_table = 'test_channel'

