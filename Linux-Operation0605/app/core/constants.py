# -*- coding: utf-8 -*-
'''
常量
'''

USER_TYPE = (
    ('systemadmin', u'系统管理员'),
    ('superadmin', u'超管'),
    ('deptadmin', u'部门管理员'),
    ('domainadmin', u'域名管理员'),
)

PROXY_CONFIG_DISABLED = (
    ("-1", u'启用'),
    ("1", u'禁用'),
)

DISABLED_STATUS = (
    ("-1", u'启用'),
    ("1", u'禁用'),
)

PROXY_SERVER_STATUS = (
    ('', u''),
    ('unconnect', u'未连接'),
    ('connected', u'已连接'),
    ('disconnected', u'连接断开'),
    ('conn_error', u'连接出错'),
)

PROXY_MOVE_TYPE = (
    ("from", u'迁入'),
    ("to", u'迁出'),
)

PROXY_MOVE_STATUS = (
    ("init", u'初始化'),
    ("wait", u'等待同步'),
    ("sync", u'正在同步'),
    ("accept", u'已接收'),
    ("ready", u'等待删帐号'),
    ("backup", u'正在备份'),
    ("ask_delete", u'开始删除帐号'),
    ("deleted", u'已删除帐号'),
    ("create", u'等待目标服创建帐号'),
    ("done", u'成功创建'),
    ("imap_recv", u'正在通过imap接收邮件'),
    ("finish", u'已完结'),
    ("unvalid", u'出错'),
)

CORE_ALIS_TYPE = (
    ('mailbox', u'邮箱'),
    ('domain', u'域名'),
    ('system', u'系统'),
    ('review', u'审核'),
)

BLACK_WHITE_OPTOR = (
    ('user', u'普通用户'),
    ('sys', u'管理员'),
)

BLACK_WHITE_TYPE = (
    ('recv', u'接收'),
    ('send', u'发送'),
)

ATTR_TYPR = (
    ('webmail', u'webmail'),
    ('system', u'system'),
)

MONITOR_LISTEN_TYPE = (
    (u'recipient', u'收信监控'),
    (u'sender', u'发信监控'),
)

MONITOR_TARGET_TYPE = (
    (u'*', u'所有'),
    (u'in', u'接收'),
    (u'out', u'外发'),
)

MONITOR_MAILMOVE_SELECT = (
    (u'1', u'监控'),
    (u'-1', u'不监控'),
)

MAILBOX_SEND_PERMIT = (
    (u"-1", u"不限制邮件发送"),
    (u"1", u"禁止发送所有邮件"),
    (u"2", u"只发送本地域邮件"),
    (u"3", u"可发送指定外域邮件"),
    (u"4", u"可发送本地所有域邮件"),
)


MAILBOX_RECV_PERMIT = (
    (u"-1", u"不限制邮件接收"),
    (u"1", u"禁止接收所有邮件"),
    (u"2", u"只接收本地域邮件"),
    (u"3", u"可接收指定外域邮件"),
    (u"4", u"可接收本地所有域邮件"),
)

MAILBOX_LIMIT_LOGIN = (
    (u"-1", u"不限制登录方式"),
    (u"1", u"禁止网页登录"),
)

MAILBOX_CHANGE_PWD = (
    (u"-1", u"不修改"),
    (u"1", u"修改"),
    (u"2", u"修改并禁用帐号"),
)

MAILBOX_ENABLE = (
    (-1, u"禁用"),
    (1, u"开启"),
)

USER_SHOW = (
    (-1, u"不显示"),
    (1, u"显示"),
)
GENDER = (
    ('male', u"男"),
    ('female', u"女"),
)
