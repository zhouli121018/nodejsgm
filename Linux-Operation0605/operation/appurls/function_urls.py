# -*- coding: utf-8 -*-
"""
系统功能设置
"""

from django.conf.urls import url
from app.setting import views as setting_views
from app.review import views as review_views
from app.distribute import views as distribute_views
from app.domain import views as domain_views
from app.maintain import views as maintain_views
from app.maillog import views as maillog_views

urlpatterns = [
    # i.	邮件域别名
    url(r'^function/alias/$', setting_views.domain_alias, name='domain_alias_set'),
    url(r'^function/alias/ajax$', setting_views.ajax_domain_alias, name='ajax_domain_alias_set'),
    url(r'^function/alias/add/$', setting_views.domain_alias_add, name='domain_alias_add'),
    url(r'^function/alias/(?P<alias_id>\d+)/$', setting_views.domain_alias_modify, name='domain_alias_modify'),

     # ii.	审核管理
    url(r'^function/review$', review_views.review_list, name='review_list'),
    url(r'^function/review/add/$', review_views.review_add, name='review_add'),
    url(r'^function/review/mdf/(?P<review_id>\d+)/$', review_views.review_modify, name='review_modify'),
    url(r'^function/review/choose/$', review_views.choose_review_list, name='choose_review_list'),

    url(r'^function/review/rule/$', review_views.reviewrule_list, name='reviewrule_list'),
    url(r'^function/review/rule/ajax/$', review_views.ajax_reviewrule_list, name='ajax_reviewrule_list'),
    url(r'^function/review/rule/add/$', review_views.reviewrule_add, name='reviewrule_add'),
    url(r'^function/review/rule/(?P<rule_id>\d+)/$', review_views.reviewrule_modify, name='reviewrule_modify'),

    url(r'^function/review/config/$', review_views.review_config, name='review_config'),

    # iii.	内容过滤器
    url(r'^function/cfilter/$', setting_views.cfilter, name='cfilter_set'),
    url(r'^function/cfilter/config/$', setting_views.cfilter_config, name='cfilter_config'),
    url(r'^function/cfilter/ajax$', setting_views.ajax_cfilter, name='ajax_cfilter_set'),
    url(r'^function/cfilter/ajax_smtp$', setting_views.ajax_smtpcheck, name='ajax_cfilter_smtpcheck'),
    url(r'^function/cfilter/add/$', setting_views.cfilter_add, name='cfilter_add_set'),
    url(r'^function/cfilter/(?P<rule_id>\d+)/$', setting_views.cfilter_modify, name='cfilter_modify_set'),
    url(r'^function/cfilter/v/(?P<rule_id>\d+)/$', setting_views.cfilter_view, name='cfilter_view_set'),

    # iv.	分布式系统
    url(r'^function/distribute/$', distribute_views.distribute_list, name='distribute_list'),
    url(r'^function/distribute/ajax$', distribute_views.ajax_distribute_list, name='ajax_distribute_list'),
    url(r'^function/distribute/add$', distribute_views.distribute_add, name='distribute_add'),
    url(r'^function/distribute/mdf/(?P<proxy_id>\d+)/$', distribute_views.distribute_modify, name='distribute_modify'),

    url(r'^function/distribute/config$', distribute_views.config, name='proxy_open_config'),

    url(r'^function/distribute/status$', distribute_views.distribute_server_status, name='distribute_server_status'),

    url(r'^function/distribute/move$', distribute_views.distribute_account_move, name='distribute_account_move'),
    url(r'^function/distribute/move/ajax$', distribute_views.ajax_distribute_move, name='ajax_distribute_move'),
    url(r'^function/distribute/move/add$', distribute_views.distribute_move_add, name='distribute_move_add'),
    url(r'^function/distribute/move/mdf/(?P<move_id>\d+)/$', distribute_views.distribute_move_modify, name='distribute_move_modify'),

    # v.	帐号间数据迁移
    url(r'^function/set/acct_transfer$', setting_views.accountTransfer, name='account_transfer'),
    url(r'^function/set/acct_transfer/add$', setting_views.accountTransferAdd, name='account_transfer_add'),
    url(r'^function/set/acct_transfer/mdf/(?P<trans_id>\d+)/$', setting_views.accountTransferModify, name='account_transfer_mdf'),
    url(r'^function/set/acct_transfer/ajax$', setting_views.ajax_accountTransfer, name='ajax_accountTransfer'),

    # v        邮件数据导入
    url(r'^function/set/mail_moving$', setting_views.imapMoving, name='mail_moving'),
    url(r'^function/set/mail_moving/add$', setting_views.imapMovingAdd, name='mail_moving_add'),
    url(r'^function/set/mail_moving/import$', setting_views.imapMovingImport, name='mail_moving_import'),
    url(r'^function/set/mail_moving/mdf/(?P<trans_id>\d+)/$', setting_views.imapMovingModify, name='mail_moving_mdf'),
    url(r'^function/set/mail_moving/ajax$', setting_views.ajax_imapMoving, name='ajax_mail_moving'),
    url(r'^function/set/mail_moving/ajax_recv$', setting_views.ajax_imapRecv, name='ajax_imaprecv'),
    url(r'^function/set/mail_moving/disable$', setting_views.imapMovingDisable, name='mail_moving_disable'),
    url(r'^function/set/mail_moving/enable$', setting_views.imapMovingEnable, name='mail_moving_enable'),
    url(r'^function/set/mail_moving/delete$', setting_views.imapMovingDelete, name='mail_moving_delete'),

    # v        邮件强制中转
    url(r'^function/set/mail_transfer/$', setting_views.mailTransfer, name='mail_transfer'),
    url(r'^function/set/mail_transfer/sender/$', setting_views.mailTransferSender, name='mail_transfer_sender'),

    url(r'^function/set/mail_transfer/post/add$', setting_views.postTransferAdd, name='post_transfer_add'),
    url(r'^function/set/mail_transfer/post/mdf/(?P<trans_id>\d+)/$', setting_views.postTransferModify, name='post_transfer_mdf'),
    url(r'^function/set/mail_transfer/post/ajax$', setting_views.ajax_postTransfer, name='ajax_post_transfer'),

    # v        邮件日志统计
    url(r'^function/maillog/$', maillog_views.mailLogView, name='maillog'),
    url(r'^function/maillog/maillog_list$', maillog_views.mailLogList, name='maillog_list'),
    url(r'^function/maillog/ajax_maillog_list$', maillog_views.ajax_maillog_list, name='ajax_maillog_list'),
    url(r'^function/maillog/mailbox_stat$', maillog_views.mailLogMailboxStat, name='maillog_mailbox_stat'),
    url(r'^function/maillog/ajax_mailbox_stat$', maillog_views.ajax_mailLogMailboxStat, name='ajax_maillog_mailbox_stat'),
    url(r'^function/maillog/active_user$', maillog_views.mailLogActiveUserStat, name='maillog_active_user'),
    url(r'^function/maillog/ajax_active_user$', maillog_views.ajax_mailLogActiveUserStat, name='ajax_maillog_active_user'),
    url(r'^function/maillog/mail_stat$', maillog_views.mailLogMailStat, name='maillog_mail_stat'),
    url(r'^function/maillog/export_active$', maillog_views.mailLogExportActive, name='maillog_export_active'),
    url(r'^function/maillog/export_mailreport$', maillog_views.mailLogExportMailReport, name='maillog_export_maillog'),
    url(r'^function/maillog/export_mailbox$', maillog_views.mailLogExportMailboxReport, name='maillog_export_mailbox'),

    # 验证
    url(r'^function/set/ajax_imapcheck$', setting_views.ajax_imapCheck, name='ajax_imapcheck'),
    url(r'^function/set/ajax_smtpcheck$', setting_views.ajax_smtpCheck, name='ajax_smtpcheck'),

    # vi.	SSL数字证书
    url(r'^function/maintain/ssl/$', maintain_views.sslView, name='ssl_maintain'),
    url(r'^function/maintain/ssl/enable$', maintain_views.sslEnableView, name='sslEnableView'),
    url(r'^function/maintain/ssl/private$', maintain_views.sslPrivateView, name='sslPrivateView'),
    url(r'^function/maintain/ssl/sign$', maintain_views.sslSignatureView, name='sslSignatureView'),
    url(r'^function/maintain/ssl/cert$', maintain_views.sslCertView, name='sslCertView'),

    # vii.	邮件头翻译
    #url(r'^function/domain/header_trans/$', domain_views.domainHeaderTrans, name='domain_header_trans'),
    #url(r'^function/domain/header_trans/ajax$', domain_views.ajax_domainHeaderTrans, name='ajax_header_trans_set'),
    #url(r'^function/domain/header_trans/add$', domain_views.domainHeaderTransAdd, name='domain_header_trans_add'),
    #url(r'^function/domain/header_trans/(?P<trans_id>\d+)/$', domain_views.domainHeaderTransModify, name='domain_header_trans_mdf'),

    # viii.	DKIM设置
    url(r'^function/set/dkim/$', setting_views.dkim, name='dkim'),
    url(r'^function/set/dkim/(?P<domain_id>\d+)/$', setting_views.dkim_modify, name='dkim_modify'),

    # ix.	杂项参数
    url(r'^function/set/setting/$', setting_views.systemSet, name='setting'),
]

__all__ = ["urlpatterns"]
