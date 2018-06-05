# -*- coding: utf-8 -*-
'''
常量
'''


# ------审核规则 ReviewRule --------

REVIEWRULE_WORKMODE = (
    (u'outbound', u'外发'),
    (u'allsend', u'所有'),
)

REVIEWRULE_LOGIC = (
    (u'all', u'满足所有条件'),
    (u'one', u'满足一条即可'),
)

REVIEWRULE_PREACTION = (
    (u'', u'人工'),
    (u'permit', u'批准'),
    (u'reject', u'拒绝'),
)

REVIEWRULE_HASATTACH = (
    (-1, u'否'),
    (1, u'是'),
)

REVIEWRULE_DISABLED = (
    (-1, u'启用'),
    (1, u'禁用'),
)

REVIEWRULE_OPTION_TYPE = (
    (u'subject', u'主题'),
    (u'date', u'邮件时间'),
    (u'recipient', u'收件人'),
    (u'sender', u'发件人'),
    (u'content', u'邮件内容'),
    (u'mail_size', u'邮件大小'),
    (u'attachment', u'附件名'),
    (u'has_attach', u'拥有附件'),
    (u'all_mail',u'所有邮件'),
)

REVIEWRULE_OPTION_TYPE_YES = (
    (u'attachment', u'附件名'),
)

REVIEWRULE_OPTION_NO_INPUT = (
    (u'has_attach', u'拥有附件'),
    (u'all_mail', u'所有邮件'),
)

REVIEWRULE_OPTION_TYPE_NO = (
    (u'subject', u'主题'),
    (u'content', u'邮件内容'),
    (u'recipient', u'收件人'),
    (u'sender', u'发件人'),
    (u'mail_size', u'邮件大小'),
    (u'date', u'邮件时间'),
)

REVIEWRULE_OPTION_CONDITION = (
    (u'contains', u'包含'),
    (u'not_contains', u'不包含'),
    (u'==', u'等于'),
    (u'>=', u'大于等于'),
    (u'<=', u'小于等于'),
)

REVIEWRULE_OPTION_CONDITION_CONTAIN = (
    (u'contains', u'包含'),
    (u'not_contains', u'不包含'),
    (u'==', u'等于'),
)

REVIEWRULE_OPTION_CONDITION_EQ = (
    (u'==', u'等于'),
    (u'>=', u'大于等于'),
    (u'<=', u'小于等于'),
)


# ------审核进度 ReviewProcess --------

REVIEWPROCESS_STATUS = (
    ('wait', u'等待'),
    ('permit', u'通过'),
    ('reject', u'拒绝')
)


# ------审核配置 ReviewConfig --------
REVIEWCONFIG_RESULT_NOTIFY_OPTION = (
    ('1', u'拒绝才发送审核结果邮件'),
    ('2', u'通过才发送审核结果邮件'),
    ('3', u'不发送审核结果邮件'),
    ('4', u'发送审核结果邮件'),
)

#这里的开关没反，涉及与旧版兼容的问题
REVIEWCONFIG_REVIEWER_NOTIFY_OPTION = (
    ('0', u'发送通知邮件给审核人'),
    ('1', u'不发送通知邮件给审核人'),
)

#审核结果邮件的默认值
REVIEWCONFIG_RESULT_NOTIFY_DEFAULT = '4'
REVIEWCONFIG_REVIEWER_NOTIFY_DEFAULT = '0'
