# -*- coding: utf-8 -*-
'''
常量
'''

import base64


DOMAIN_BASIC_PARAMS = (
    (u"cf_limit_mailbox_cnt", u"限定邮箱数量"),
    (u"cf_limit_alias_cnt", u"限定别名数量"),
    (u"cf_limit_mailbox_size", u"限定邮箱空间总容量"),
    (u"cf_limit_netdisk_size", u"限定网络硬盘总容量"),
    (u"cf_limit_email_size", u"发送邮件限制大小"),
    (u"cf_limit_attach_size", u"超大附件限制大小"),
    (u"cf_def_mailbox_size", u"用户邮箱默认容量"),
    (u"cf_def_netdisk_size", u"网络硬盘默认容量"),
)

DOMAIN_BASIC_PARAMS_VALUE = (
    (u"cf_limit_mailbox_cnt",     "8000"),
    (u"cf_limit_alias_cnt",       "0"),
    (u"cf_limit_mailbox_size",   "0"),
    (u"cf_limit_netdisk_size",   "500"),
    (u"cf_limit_email_size",     "0"),
    (u"cf_limit_attach_size",    "10"),
    (u"cf_def_mailbox_size",     "100"),
    (u"cf_def_netdisk_size",     "100"),
)

DOMAIN_BASIC_PARAMS_TYPE = (
    (u"cf_limit_mailbox_cnt",   "system"),
    (u"cf_limit_alias_cnt",   "system"),
    (u"cf_limit_mailbox_size",   "system"),
    (u"cf_limit_netdisk_size",   "system"),
    (u"cf_limit_email_size",   "system"),
    (u"cf_limit_attach_size",   "system"),
    (u"cf_def_mailbox_size",   "system"),
    (u"cf_def_netdisk_size",   "system"),
)

DOMAIN_BASIC_STATUS = (
    (u"mailboxUsed", u"已分配邮箱"),
    (u"aliasUsed", u"已分配别名"),
    (u"spaceUsed", u"已分配邮箱空间"),
    (u"netdiskUsed", u"已分配网盘空间"),
)

DOMAIN_REG_LOGIN_PARAMS = (
    (u"sw_user_reg", u"用户申请邮箱功能"),
    (u"sw_reg_ratify", u"管理员审核开通"),
    (u"sw_link_admin", u"管理员登陆链接显示在邮件系统登陆页"),
    (u"sw_welcome_letter", u"新用户欢迎信功能"),
    (u"sw_agreement", u"新用户欢迎信功能"),
)

DOMAIN_REG_LOGIN_VALUE = (
    (u"sw_user_reg",         "-1"),
    (u"sw_reg_ratify",       "-1"),
    (u"sw_link_admin",       "1"),
    (u"sw_welcome_letter",   "1"),
    (u"sw_agreement",         "1"),
)

DOMAIN_REG_LOGIN_TYPE = (
    (u"sw_user_reg",            "webmail"),
    (u"sw_reg_ratify",          "webmail"),
    (u"sw_link_admin",          "webmail"),
    (u"sw_welcome_letter",      "system"),
    (u"sw_agreement",            "webmail"),
)

DOMAIN_REG_LOGIN_WELCOME_PARAMS = (
    (u"cf_welcome_letter", u"欢迎信内容"),
)

DOMAIN_REG_LOGIN_WELCOME_VALUE = (
    (u"cf_welcome_letter",  ""),
)

DOMAIN_REG_LOGIN_WELCOME_TYPE = (
    (u"cf_welcome_letter",      "system"),
)

DOMAIN_REG_LOGIN_AGREE_PARAMS = (
    (u"cf_agreement", u"用户注册协议"),
)

DOMAIN_REG_LOGIN_AGREE_VALUE = (
    (u"cf_agreement",  ""),
)

DOMAIN_REG_LOGIN_AGREE_TYPE = (
    (u"cf_agreement",      "webmail"),
)

DOMAIN_SYS_RECV_PARAMS = (
    (u"limit_send", u"发信功能限制"),
    (u"limit_recv", u"收信功能限制"),
    (u"limit_pop", u"POP/POPS邮箱收取功能"),
    (u"limit_imap", u"IMAP/IMAPS客户端邮件收发功能"),
    (u"limit_smtp", u"SMTP/SMTPS客户端邮件发送功能"),
)

DOMAIN_SYS_RECV_VALUE = (
    (u"limit_send", u"-1"),
    (u"limit_recv", u"-1"),
    (u"limit_pop", u"-1"),
    (u"limit_imap", u"-1"),
    (u"limit_smtp", u"-1"),
)

DOMAIN_SYS_RECV_TYPE = (
    (u"limit_send", u"system"),
    (u"limit_recv", u"system"),
    (u"limit_pop", u"system"),
    (u"limit_imap", u"system"),
    (u"limit_smtp", u"system"),
)

DOMAIN_SYS_SECURITY_PARAMS = (
    (u"sw_def_login_limit_mail", u"开启修改密码通知信"),
    (u"cf_def_safe_login", u"安全登录限制"),
    (u"admin_login_switch", u"管理员登录密码错误3次锁定登录IP"),
)

DOMAIN_SYS_SECURITY_VALUE = (
    (u"sw_def_login_limit_mail", u"1"),
    (u"cf_def_safe_login", u""),
    (u"admin_login_switch", u"-1"),
)

DOMAIN_SYS_SECURITY_TYPE = (
    (u"sw_def_login_limit_mail", u"system"),
    (u"cf_def_safe_login", u"webmail"),
    (u"admin_login_switch", u"system"),
)

DOMAIN_SYS_SECURITY_PWD_PARAMS = (
    (u"cf_def_login_limit_mail", u"修改密码通知信"),
)

DOMAIN_SYS_SECURITY_PWD_VALUES = (
    (u"cf_def_login_limit_mail", u""),
)

DOMAIN_SYS_SECURITY_PWD_TYPE = (
    (u"cf_def_login_limit_mail", u"system"),
)

DOMAIN_SYS_PASSWORD_PARAMS = (
    (u"sw_pwdtimeout", u"定期密码修改设置"),
    (u"cf_pwd_days", u"密码有效期间"),
    (u"cf_pwd_days_time", u"密码有效开始时间"),
    (u"cf_first_change_pwd", u"首次登录修改密码"),
    (u"cf_pwd_type", u"密码组成字符种类"),
    (u"cf_pwd_rule", u"其他密码规则设置"),
)

DOMAIN_SYS_PASSWORD_VALUE = (
    (u"sw_pwd_timeout", u"1"),
    (u"cf_pwd_days", u"365"),
    (u"cf_pwd_days_time", u"0"),
    (u"cf_first_change_pwd", u"-1"),
    (u"cf_pwd_type", u"-1"),
    (u"cf_pwd_rule", u""),
)

DOMAIN_SYS_PASSWORD_TYPE = (
    (u"sw_pwd_timeout", u"system"),
    (u"cf_pwd_days", u"system"),
    (u"cf_pwd_days_time", u"system"),
    (u"cf_first_change_pwd", u"system"),
    (u"cf_pwd_type", u"system"),
    (u"cf_pwd_rule", u"system"),
)

#密码组成字符种类
DOMAIN_SYS_PASSWORD_TYPE_LIMIT = (
    (u"-1", u"必须包含两种字符"),
    (u"1", u"必须包含三种字符"),
    (u"2", u"必须包含四种字符"),
)

#其他密码规则设置
DOMAIN_SYS_PASSWORD_RULE_VALUE = (
    (u"pwdLen", u"len"),
    (u"pwdLenValue", u"len_value"),
    (u"pwdNoAcct", u"no_acct"),
    (u"pwdNumLimit", u"num_limit"),
    (u"pwdWordLimit", u"word_limit"),
    (u"pwdFlagLimit", u"flag_limit"),
    (u"pwdNoName", u"no_name"),
)

DOMAIN_SYS_PASSWORD_LEN_LIMIT = tuple([u"{}".format(v) for v in range(8,17)])

DOMAIN_SYS_PASSWORD_RULE_LIMIT = (
    #是否限制密码长度
    (u"len",    u"1"),
    #密码长度的值
    (u"len_value",    u"16"),
    #密码不能包含账号
    (u"no_acct",    u"1"),
    #连续3位及以上数字不能连号
    (u"num_limit",    u"1"),
    #连续3位及以上字母不能连号
    (u"word_limit",    u"1"),
    #密码不能包含连续3个及以上相同字符
    (u"flag_limit",    u"1"),
    #密码不能包含用户姓名大小写全拼
    (u"no_name",    u"1"),
)

DOMAIN_SYS_INTERFACE_PARAMS = (
    (u"sw_auth_api", u"第三方登录验证"),
    (u"sw_api_pwd_encry", u"接口修改密码是否加密"),
    (u"sw_impush", u"即时通讯软件集成"),
    (u"sw_xss_token", u"登录防止xss启用token验证"),
)

DOMAIN_SYS_INTERFACE_VALUE = (
    (u"sw_auth_api",        u"-1"),
    (u"sw_api_pwd_encry",  u"-1"),
    (u"sw_impush",          u"-1"),
    (u"sw_xss_token",       u"-1"),
)

DOMAIN_SYS_INTERFACE_TYPE = (
    (u"sw_auth_api",        u"webmail"),
    (u"sw_api_pwd_encry",  u"webmail"),
    (u"sw_impush",          u"webmail"),
    (u"sw_xss_token",       u"webmail"),
)

DOMAIN_SYS_INTERFACE_AUTH_API_VALUE = (
    (u"cf_auth_api",        u""),
)

DOMAIN_SYS_INTERFACE_AUTH_API_TYPE = (
    (u"cf_auth_api",        u"webmail"),
)

DOMAIN_SYS_INTERFACE_IM_API_VALUE = (
    (u"cf_impush_api",        u""),
)

DOMAIN_SYS_INTERFACE_IM_API_TYPE = (
    (u"cf_impush_api",        u"webmail"),
)

DOMAIN_SYS_OTHERS_PARAMS = (
    (u"sw_full_reject",        u"邮箱容量满后拒绝接收邮件"),
    (u"sw_auto_clean",         u"邮箱空间定时清理功能"),
    (u"sw_client_attach",      u"客户端在线附件开关"),
    (u"sw_auto_inbox",          u"登录默认打开收件箱"),
    (u"sw_filter_duplicate_mail",    u"收件时是否过滤重复邮件"),
    (u"sw_display_list",       u"邮件列表发来邮件显示邮件列表名称"),
    (u"sw_smscode",            u"短信通知功能"),
)

DOMAIN_SYS_OTHERS_VALUE = (
    (u"sw_full_reject",        u"1"),
    (u"sw_auto_clean",         u"1"),
    (u"sw_client_attach",      u"1"),
    (u"sw_auto_inbox",          u"1"),
    (u"sw_filter_duplicate_mail",    u"1"),
    (u"sw_display_list",       u"1"),
    (u"sw_smscode",            u"-1"),
)

DOMAIN_SYS_OTHERS_TYPE = (
    (u"sw_full_reject",        u"webmail"),
    (u"sw_auto_clean",         u"webmail"),
    (u"sw_client_attach",      u"webmail"),
    (u"sw_auto_inbox",          u"webmail"),
    (u"sw_filter_duplicate_mail",    u"webmail"),
    (u"sw_display_list",       u"webmail"),
    (u"sw_smscode",            u"webmail"),
)

DOMAIN_SYS_OTHERS_SPACE_VALUE = (
    (u"cf_spaceclean",        u""),
    (u"cf_spacemail",         u""),
)

DOMAIN_SYS_OTHERS_SPACE_TYPE = (
    (u"cf_spaceclean",        u"system"),
    (u"cf_spacemail",         u"system"),
)

DOMAIN_SYS_OTHERS_ATTACH_VALUE = (
    (u"cf_client_size",        u"50"),
    (u"cf_client_url",         u""),
)

DOMAIN_SYS_OTHERS_ATTACH_TYPE = (
    (u"cf_client_size",        u"webmail"),
    (u"cf_client_url",         u"webmail"),
)

DOMAIN_SIGN_PARAMS = (
    (u'cf_domain_signature',u'域签名'),
)

DOMAIN_SIGN_VALUE = (
    (u'cf_domain_signature',u''),
)

DOMAIN_SIGN_TYPE = (
    (u'cf_domain_signature',u'system'),
)

DOMAIN_SIGN_PERSONAL_PARAMS = (
    (u'cf_personal_sign',u'个人签名模板'),
)

DOMAIN_SIGN_PERSONAL_VALUE = (
    (u'cf_personal_sign',u''),
)

DOMAIN_SIGN_PERSONAL_TYPE = (
    (u'cf_personal_sign',u'webmail'),
)

# ------个人签名 的输入参数 --------
DOMAIN_PERSONAL_DEFAULT_CODE = """<p><span style="font-size:16px;"><strong>{NAME}&nbsp; [<span style="font-size:14px;">{POSITION}</span>]<br /></strong></span></p><p><span style="white-space:normal;font-size:16px;"><strong>{TELEPHONE}</strong></span></p><p><br /><strong></strong></p><p><span style="font-size:14px;"><strong>这里填公司名称<br /></strong></span></p><p>地址：这里填公司地址</p><p>电话：<span style="white-space:normal;">{WORKPHONE}&nbsp;&nbsp; 传真：这里填传真号码&nbsp; 邮箱：{EMAIL}<br /></span></p><br /><p><span style="white-space:normal;"><br /></span></p>"""
DOMAIN_PERSONAL_DEFAULT_CODE=base64.encodestring(DOMAIN_PERSONAL_DEFAULT_CODE)
DOMAIN_PERSONAL_DEFAULT_CODE=u"{}".format(DOMAIN_PERSONAL_DEFAULT_CODE)
DOMAIN_SIGN_PERSONAL_VALUE_DEFAULT = (
    (u'personal_sign_new',u'-1'),
    (u'personal_sign_forward',u'-1'),
    (u'personal_sign_auto',u'1'),
    (u'personal_sign_templ',DOMAIN_PERSONAL_DEFAULT_CODE),
)

DOMAIN_MODULE_HOME_PARAMS = (
    (u'sw_business_tools', u'商务小工具栏目'),
    (u'sw_wgt_cale', u'万年历'),
    (u'sw_wgt_calc', u'万用计算器'),
    (u'sw_wgt_maps', u'城市地图'),

    (u'sw_email_used_see', u'用户已用邮箱容量查看功能'),
    (u'sw_weather', u'天气预报功能'),
    (u'sw_oab', u'企业通讯录'),
    (u'sw_cab', u'公共通讯录'),
    (u'sw_oab_share', u'其他域通讯录共享'),
    (u'sw_oab_dumpbutton', u'通讯录导出按钮开关'),

    (u'sw_department_openall', u'企业通讯录域组合'),
    (u'sw_dept_showall', u'父部门中是否显示子部门邮件账号'),
    (u'sw_netdisk', u'网络硬盘功能'),
    (u'sw_calendar', u'日程功能'),
    (u'sw_notes', u'便签功能'),
)

DOMAIN_MODULE_HOME_VALUE = (
    (u'sw_business_tools', u'1'),
    (u'sw_wgt_cale', u'1'),
    (u'sw_wgt_calc', u'1'),
    (u'sw_wgt_maps', u'1'),

    (u'sw_email_used_see', u'1'),
    (u'sw_weather', u'1'),
    (u'sw_oab', u'-1'),
    (u'sw_cab', u'-1'),
    (u'sw_oab_share', u'-1'),
    (u'sw_oab_dumpbutton', u'-1'),

    (u'sw_department_openall', u'-1'),
    (u'sw_dept_showall', u'-1'),
    (u'sw_netdisk', u'1'),
    (u'sw_calendar', u'1'),
    (u'sw_notes', u'1'),
)

DOMAIN_MODULE_HOME_TYPE = (
    (u'sw_business_tools', u'webmail'),
    (u'sw_wgt_cale', u'webmail'),
    (u'sw_wgt_calc', u'webmail'),
    (u'sw_wgt_maps', u'webmail'),

    (u'sw_email_used_see', u'webmail'),
    (u'sw_weather', u'webmail'),
    (u'sw_oab', u'webmail'),
    (u'sw_cab', u'webmail'),
    (u'sw_oab_share', u'webmail'),
    (u'sw_oab_dumpbutton', u'webmail'),

    (u'sw_department_openall', u'webmail'),
    (u'sw_dept_showall', u'webmail'),
    (u'sw_netdisk', u'webmail'),
    (u'sw_calendar', u'webmail'),
    (u'sw_notes', u'webmail'),
)

DOMAIN_MODULE_MAIL_PARAMS = (
    (u'sw_drafts', u'保存草稿功能'),
    (u'sw_mail_encryption', u'发送邮件显示加密选项'),
    (u'sw_show_add_paper', u'显示地址簿和信纸模块'),
    (u'sw_mailpaper', u'去掉信纸模块'),

    (u'sw_auto_receipt', u'自动发送回执功能'),
    (u'sw_mail_in_reply_to', u'添加Reply-To到邮件头'),
)

DOMAIN_MODULE_MAIL_VALUE = (
    (u'sw_drafts', u'1'),
    (u'sw_mail_encryption', u'1'),
    (u'sw_show_add_paper', u'-1'),
    (u'sw_mailpaper', u'-1'),

    (u'sw_auto_receipt', u'1'),
    (u'sw_mail_in_reply_to', u'1'),
)

DOMAIN_MODULE_MAIL_TYPE = (
    (u'sw_drafts', u'webmail'),
    (u'sw_mail_encryption', u'webmail'),
    (u'sw_show_add_paper', u'webmail'),
    (u'sw_mailpaper', u'webmail'),

    (u'sw_auto_receipt', u'webmail'),
    (u'sw_mail_in_reply_to', u'webmail'),
)

DOMAIN_MODULE_SET_PARAMS = (
    (u'sw_change_userinfo', u'个人资料功能'),
    (u'sw_change_pass', u'密码修改功能'),
    (u'sw_options', u'参数设置功能'),
    (u'sw_signature', u'邮件签名功能'),

    (u'sw_auto_reply', u'自动回复功能'),
    (u'sw_auto_forward', u'自动转发功能'),
    #(u'sys_userbwlist', u'黑白名单功能'),
    (u'sw_autoforward_visible', u'设置自动转发默认值'),
    (u'sw_mailboxmove', u'邮箱搬家功能'),
    (u'sw_feedback', u'邮箱意见反馈功能'),

    (u'sw_zhaohui', u'邮件召回记录查看'),
    (u'sw_cfilter', u'邮件过滤功能'),
    (u'sw_smtptransfer_visible', u'SMTP外发邮件代理'),
)

DOMAIN_MODULE_SET_VALUE = (
    (u'sw_change_userinfo', u'1'),
    (u'sw_change_pass', u'1'),
    (u'sw_options', u'1'),
    (u'sw_signature', u'1'),

    (u'sw_auto_reply', u'1'),
    (u'sw_auto_forward', u'1'),
    #(u'userbwlist', u'黑白名单功能'),
    (u'sw_autoforward_visible', u'1'),
    (u'sw_mailboxmove', u'1'),
    (u'sw_feedback', u'1'),

    (u'sw_zhaohui', u'1'),
    (u'sw_cfilter', u'1'),
    (u'sw_smtptransfer_visible', u'-1'),
)

DOMAIN_MODULE_SET_TYPE = (
    (u'sw_change_userinfo', u'webmail'),
    (u'sw_change_pass', u'webmail'),
    (u'sw_options', u'webmail'),
    (u'sw_signature', u'webmail'),

    (u'sw_auto_reply', u'webmail'),
    (u'sw_auto_forward', u'webmail'),
    #(u'userbwlist', u'-1'),
    (u'sw_autoforward_visible', u'webmail'),
    (u'sw_mailboxmove', u'webmail'),
    (u'sw_feedback', u'webmail'),

    (u'sw_zhaohui', u'webmail'),
    (u'sw_cfilter', u'webmail'),
    (u'sw_smtptransfer_visible', u'webmail'),
)

DOMAIN_MODULE_OTHER_PARAMS = (
    (u'sw_folder_clean', u'清空文件夹功能'),
    (u'sw_realaddress_alert', u'代发邮件地址提醒'),
    (u'sw_time_mode', u'邮件内容中时间显示'),
    #(u'sw_user_score', u'用户积分功能'),
    (u'sw_dept_maillist', u'部门邮件列表'),
)

DOMAIN_MODULE_OTHER_VALUE = (
    (u'sw_folder_clean', u'1'),
    (u'sw_realaddress_alert', u'1'),
    (u'sw_time_mode', u'1'),
    #(u'sw_user_score', u'1'),
    (u'sw_dept_maillist', u'-1'),
)

DOMAIN_MODULE_OTHER_TYPE = (
    (u'sw_folder_clean', u'webmail'),
    (u'sw_realaddress_alert', u'webmail'),
    (u'sw_time_mode', u'webmail'),
    #(u'sw_user_score', u'webmail'),
    (u'sw_dept_maillist', u'webmail'),
)

DOMAIN_SECRET_GRADE_1 = u'0'   #秘密
DOMAIN_SECRET_GRADE_2 = u'1'   #机密
DOMAIN_SECRET_GRADE_3 = u'2'   #绝密

DOMAIN_SECRET_GRADE_ALL = (
    (DOMAIN_SECRET_GRADE_1, u"秘密"),
    (DOMAIN_SECRET_GRADE_2, u"机密"),
    (DOMAIN_SECRET_GRADE_3, u"绝密"),
)
