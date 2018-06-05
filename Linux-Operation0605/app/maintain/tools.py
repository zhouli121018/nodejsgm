# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random
import json
import uuid
from django_redis import get_redis_connection
from lib.formats import dict_compatibility

def generateRedisTaskID():
    return "{:0>5d}-{}".format(random.randint(1, 10000), uuid.uuid1())

LOG_DESC = {
    'authenticator': u'帐号验证日志',
    'rulefilter':  u'SMTP会话规则过滤程序日志',
    'receiver':    u'邮件接收程序日志',
    'dispatcher':  u'任务调度程序日志',
    'sizequerier': u'邮箱空间使用大小查询程序日志',

    # 邮件收发相关程序
    'router'    :  u'邮件路由程序日志',
    'review'    :  u'邮件审核程序日志',
    'incheck'   :  u'入站反病毒、反垃圾检测程序日志',
    'postman'   :  u'本地邮件投递程序日志',
    'maillist'  :  u'邮件列表处理程序日志',
    'forward'   :  u'自动转发程序日志',
    'outcheck'  :  u'出站反病毒、反垃圾检测程序日志',
    'smtp'      :  u'SMTP外发程序日志',
    'reply'     :  u'自动回复程序日志',
    'popmail'   :  u'POP邮件接收程序日志',
    'imapmail'   :  u'IMAP邮件接收程序日志',
    'recall'    :  u'邮件召回程序日志',
    'sequester' :   u'邮件隔离日志',

    # 邮件通知推送相关程序
    'impush'    :  u'IM信息推送程序日志',
    'smsnotice' :  u'短信通知程序日志',

    # 其它维护程序
    'upgrade'   : u'升级程序日志',
    'userinit'  : u'邮箱帐号初始化程序日志',
    'cleaner'   : u'邮箱帐号数据清除程序日志',
    'backup'    : u'数据备份程序日志',
    'restore'   : u'备份数据恢复程序日志',
    'spacescan' : u'邮箱空间清理程序日志',
    'ldapsync'  : u'远程LDAP数据同步日志',
    'ldap_server' : u'本地LDAP数据同步日志',
    'proxy_monitor' : u'分布式进程监控日志',
    'proxy_main' : u'分布式主进程日志',
    'update_spam_resource' : u'反垃圾库更新日志',
    'account_transfer' : u'禁用帐号数据迁移日志',
    'netdisk_attach' : u'客户端在线附件转存日志',
    'smtp_monitor' : u'SMTP外发监控日志',
    'search_scaner' : u'邮件搜索缓存日志',
    'search_server' : u'邮件搜索查询日志',
    'upgrade_database' : u'数据库更新日志',
    'proxy_version_modify' : u'分布式数据库更新日志',
    'task_monitor' : u'临时任务调度日志(root权限)',
    'error'     : u'错误日志汇总',
}

def getLogDesc(logname):
    name = logname.split(".")[0]
    return dict_compatibility(LOG_DESC, name, "")


from collections import namedtuple
# 备份数据格式
BackupFormat = namedtuple("Backup", ['index', 'file', 'names', 'size', "times"])
# 日志格式
LogFormat = namedtuple("Log", ['index', 'name', 'desc', 'size'])


# def getTableodd(index):
#     if index%2:
#         return True
#     return False
