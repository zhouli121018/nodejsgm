#coding=utf-8

from django.utils.translation import ugettext_lazy as _

IS_REGISTER_CHOICE = (
    (0, u'非自主注册用户(一般)'),
    (1, u'支付宝用户（测试）'),
    (2, u'支付宝转正式用户'),
)

CHOICE_0_1 = (
    ('0', '0'),
    ('1', '1'),
)

SERVER_TYPE = (
    ('0', _(u'正式服务器')),
    ('1', _(u'测试服务器')),
    ('2', _(u'SMTP测试通道')),
    ('3', '3'),
    ('4', '4'),
    ('5', _(u'正式服务器(不走测试通道)')),
    ('6', _(u'U-Mail测试用户')),
)

SEND_TYPE = (
    ('local', 'local'),
    ('remote', 'remote'),
)

SERVICE_TYPE = (
    ('all', 'all'),
    ('day', 'day'),
)

STATUS = (
    ('Y', _(u'是')),
    ('N', _(u'否')),
)

DISABLED = (
    ('0', _(u'正常')),
    ('1', _(u'禁用')),
)


USER_TYPE = (
    ('', u'--'),
    ('users', _(u'普通用户')),
    ('manager', _(u'管理员')),
    ('system', _(u'系统')),
    ('super', _(u'超级用户')),
    ('agents', _(u'代理用户')),
)

ACTION_TYPE = (
    ('add_account', _(u'添加群发帐户')),
    ('edit_account', _(u'修改帐户信息')),
    ('del_account', _(u'删除群发帐户')),
    ('init_service', _(u'初始化群发服务')),

    ('set_service', _(u'更改群发服务设置')),
    ('add_ip', _(u'添加IP地址')),
    ('del_ip', _(u'删除IP地址')),
    ('add_domain', _(u'添加域名')),
    ('del_domain', _(u'删除域名')),
    ('add_mailbox', _(u'添加发送帐号')),
    ('set_mailbox', _(u'修改发送帐号')),
    ('del_mailbox', _(u'删除发送帐号')),
    ('update_count', _(u'客服充值')),
    ('c_update_count', _(u'自助充值')),
    ('sys_auto_return', _(u'系统自动返量')),
    ('disable_account', _(u'删除群发帐户')),
    ('recover_account', _(u'恢复群发帐户')),
    ('user_login', _(u'登录日志')),

    ('add_subuser', _(u'添加子账户')),
    ('recharge_subuser', _(u'子账户充值')),
)

SEX_CHOICES = (
    ('1', _(u'男')),
    ('2', _(u'女')),
)

CUSTOMER_DOMAIN_STATUS = (
    ('Y', _(u'验证通过')),
    ('T', _(u'验证通过')), #不进行自动检测
    ('N', _(u'待验证')),
    ('A', _(u'验证未通过(自动检测)')),
    ('f', _(u'验证未通过')),
)

PAY_WAY = (
    ('wxpay', _(u'微信支付')),
    ('alipay', _(u'支付宝支付'))
)

ORDER_STATUS = (
    ('waiting', _(u'等待付款')),
    ('paied', _(u'已付款')),
    ('lapsed', _(u'已失效')),
    ('cancel', _(u'已取消')),
    ('yesapply', _(u'已申请发票')),
    ('notapply', _(u'未申请发票')),
)

INVOICE_STATUS = (
    ('apply', _(u'申请中')),
    ('invoiced', _(u'已开票')),
    ('wait', _(u'等待快递')),
    ('sent', _(u'已发快递')),
)

INVOICE_TYPE = (
    ('1', _(u'增值税普通发票')),
    ('2', _(u'增值税专用发票')),
)

ESTIMATE_SELECT = (
    ('1', _(u'2万以下')),
    ('2', _(u'2-12万')),
    ('3', _(u'12-50万')),
    ('4', _(u'50万以上')),
    ('5', _(u'100万以上')),
    ('6', _(u'200万以上')),
)

CONTENT_SELECT = (
    ('1', _(u'营销')),
    ('2', _(u'开发信')),
    ('3', _(u'注册信')),
    ('4', _(u'验证码')),
    ('5', _(u'期刊')),
    ('6', _(u'其他')),
)

INDUSTRY_SELECT = (
    ('1', _(u'电子商务')),
    ('2', _(u'社区论坛')),
    ('3', _(u'游戏')),
    ('4', _(u'人力资源')),
    ('5', _(u'IT服务')),
    ('6', _(u'体育健康')),
    ('7', _(u'培训教育')),
    ('8', _(u'艺术文学')),
    ('9', _(u'金融')),
    ('10', _(u'物流')),
    ('11', _(u'其他')),
)

WAY_SELECT = (
    ('1', _(u'搜索引擎')),
    ('2', _(u'广告推广')),
    ('3', _(u'媒体报道')),
    ('4', _(u'社交平台')),
    ('5', _(u'朋友推荐')),
    ('6', _(u'其他')),
)

WEB_STYLE = (
    ('0', _(u'默认黑')),
    ('3', _(u'商务白')),
)
AUTOREMOVE_TYPE = (
    (0, _(u'暂未开启')),
    (1, _(u'开启')),
)

DUPLICATE_TYPE = (
    ('new', u'保留之前的重复地址'),
    ('old', u'保留最新导入的重复地址'),
)

IS_SHEAR_FLAG = (
    ('1', _(u'母账户')),
    ('2', _(u'不共享')),
    ('3', _(u'部分共享')),
    ('4', _(u'全部共享')),
)


NOTIFICATION_TYPE = [
    ('1', _(u'异地登录')),
    ('2', _(u'充值成功')),
    ('3', _(u'域名解析异常')),
    ('4', _(u'邮件审核不通过')),
    ('5', _(u'余额到达警戒值')),
    ('6', _(u'联系人信息修改')),
    # 暂时不用
    # ('1', _(u'异常消费提醒')),
    # ('4', _(u'信誉度降低提醒')),
]
