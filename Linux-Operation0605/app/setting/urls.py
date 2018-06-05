# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.systemSet, name='system_set'),
    # url(r'^trustip/$', views.trustip_set, name='trustip_set'),
    # url(r'^trustip/ajax$', views.ajax_trustip_set, name='ajax_trustip_set'),
    # url(r'^dkim/$', views.dkim, name='dkim'),
    # url(r'^dkim/(?P<domain_id>\d+)/$', views.dkim_modify, name='dkim_modify'),
    # url(r'^black/$', views.blacklist, name='blacklist_set'),
    # url(r'^black/ajax$', views.ajax_blacklist, name='ajax_blacklist_set'),
    # url(r'^white/$', views.whitelist, name='whitelist_set'),
    # url(r'^white/ajax$', views.ajax_whitelist, name='ajax_whitelist_set'),
    # url(r'^white_rcp/$', views.whitelist_rcp, name='whitelist_rcp_set'),
    # url(r'^white_rcp/ajax$', views.ajax_whitelist_rcp, name='ajax_whitelist_rcp_set'),

    # url(r'^alias/$', views.domain_alias, name='domain_alias_set'),
    # url(r'^alias/ajax$', views.ajax_domain_alias, name='ajax_domain_alias_set'),
    # url(r'^alias/add/$', views.domain_alias_add, name='domain_alias_add'),
    # url(r'^alias/(?P<alias_id>\d+)/$', views.domain_alias_modify, name='domain_alias_modify'),

    # url(r'^cfilter/$', views.cfilter, name='cfilter_set'),
     url(r'^cfilter/config/$', views.cfilter_config, name='cfilter_config'),
    # url(r'^cfilter/ajax$', views.ajax_cfilter, name='ajax_cfilter_set'),
    # url(r'^cfilter/ajax_smtp$', views.ajax_smtpcheck, name='ajax_cfilter_smtpcheck'),
    # url(r'^cfilter/add/$', views.cfilter_add, name='cfilter_add_set'),
    # url(r'^cfilter/(?P<rule_id>\d+)/$', views.cfilter_modify, name='cfilter_modify_set'),
    # url(r'^cfilter/v/(?P<rule_id>\d+)/$', views.cfilter_view, name='cfilter_view_set'),

    url(r'^smtp/$', views.smtp, name='smtp_set'),

    # url(r'^acct_transfer$', views.accountTransfer, name='account_transfer'),
    # url(r'^acct_transfer/add$', views.accountTransferAdd, name='account_transfer_add'),
    # url(r'^acct_transfer/mdf/(?P<trans_id>\d+)/$', views.accountTransferModify, name='account_transfer_mdf'),
    # url(r'^acct_transfer/ajax$', views.ajax_accountTransfer, name='ajax_accountTransfer'),
]
