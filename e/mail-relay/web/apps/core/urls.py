from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'customer_list$', 'apps.core.views.customer_list', name='customer_list'),
    url(r'ajax_get_customers$', 'apps.core.views.ajax_get_customers', name='ajax_get_customers'),
    url(r'customer/(?P<customer_id>\d+)/$', 'apps.core.views.customer_modify', name='customer_modify'),
    url(r'customer_setting/(?P<customer_id>\d+)/$', 'apps.core.views.customer_setting', name='customer_setting'),
    url(r'customer_localized_setting/(?P<customer_id>\d+)/$', 'apps.core.views.customer_localized_setting', name='customer_localized_setting'),
    url(r'customer/add/$$', 'apps.core.views.customer_add', name='customer_add'),
    url(r'customer/batchadd/$$', 'apps.core.views.customer_batchadd', name='customer_batchadd'),

    url(r'ajax_get_customer_summary$', 'apps.core.views.ajax_get_customer_summary', name='ajax_get_customer_summary'),
    url(r'^customer_summary$', 'apps.core.views.customer_summary', name='customer_summary'),


    url(r'customer/(?P<customer_id>\d+)/password/$', 'apps.core.views.customer_password_modify', name='customer_password_modify'),
    url(r'customer/ip/(?P<customer_id>\d+)/$$', 'apps.core.views.customer_ip', name='customer_ip'),
    url(r'customer/ip/(?P<customer_id>\d+)/change_status/$', 'apps.core.views.customer_ip_change_status', name='customer_ip_change_status'),

    url(r'customer/domain/(?P<customer_id>\d+)/$$', 'apps.core.views.customer_domain', name='customer_domain'),
    url(r'customer/domain/(?P<customer_id>\d+)/change_status/$', 'apps.core.views.customer_domain_change_status', name='customer_domain_change_status'),

    url(r'customer/mailbox/(?P<customer_id>\d+)/$$', 'apps.core.views.customer_mailbox', name='customer_mailbox'),
    url(r'customer/maibox/(?P<customer_id>\d+)/change_status/$', 'apps.core.views.customer_mailbox_change_status', name='customer_mailbox_change_status'),

    url(r'cluster_list$', 'apps.core.views.cluster_list', name='cluster_list'),
    url(r'cluster/add/$', 'apps.core.views.cluster_add', name='cluster_add'),
    url(r'cluster/(?P<cluster_id>\d+)/$', 'apps.core.views.cluster_modify', name='cluster_modify'),
    url(r'cluster/(?P<cluster_id>\d+)/ip_list$', 'apps.core.views.ip_list', name='ip_list'),
    url(r'cluster/(?P<cluster_id>\d+)/ip_add$', 'apps.core.views.ip_add', name='ip_add'),

    url(r'ip_pool_list$', 'apps.core.views.ip_pool_list', name='ip_pool_list'),
    url(r'ip_pool/(?P<ip_pool_id>\d+)/$', 'apps.core.views.ip_pool_modify', name='ip_pool_modify'),
    url(r'ip_pool/add/$', 'apps.core.views.ip_pool_add', name='ip_pool_add'),

    url(r'route_rule_list/(?P<ip_pool_id>\d+)/$', 'apps.core.views.route_rule_list', name='route_rule_list'),
    url(r'route_rule/(?P<id>\d+)/$', 'apps.core.views.route_rule_modify', name='route_rule_modify'),
    url(r'route_rule/add/$', 'apps.core.views.route_rule_add', name='route_rule_add'),

    url(r'customer/col_domain/$', 'apps.core.views.col_customer_domain', name='colcustomer_domain'),
    url(r'customer/col_domain/(?P<customer_id>\d+)/(?P<domain_id>\d+)/$', 'apps.core.views.col_customer_domain_modify', name='colcustomer_domain_modify'),
    url(r'customer/col_domain_batchadd/(?P<customer_id>\d+)/$', 'apps.core.views.col_customer_domain_batchadd', name='colcustomer_domain_batchadd'),
    url(r'customer/col_domain/(?P<customer_id>\d+)/change_status/$', 'apps.core.views.col_customer_domain_change_status', name='colcustomer_domain_change_status'),
    url(r'postfix_status$', 'apps.core.views.postfix_status', name='postfix_status'),
    url(r'^get_postfix_search$', 'apps.core.views.get_postfix_search', name='get_postfix_search'),
    url(r'^postfix_search$', 'apps.core.views.postfix_search', name='postfix_search'),

    url(r'notice_list/$', 'apps.core.views.notice_list', name='notice_list'),
    url(r'ajax_get_notices$', 'apps.core.views.ajax_get_notices', name='ajax_get_notices'),
    url(r'notice_history/$', 'apps.core.views.notice_history', name='notice_history'),
    url(r'ordered_model/(?P<app>.+)/(?P<model>.+)/(?P<id>\d+)/(?P<move>.+)$', 'apps.core.views.ordered_model', name='ordered_model'),
    url(r'batch_ordered_model/(?P<app>.+)/(?P<model>.+)$', 'apps.core.views.batch_ordered_model', name='batch_ordered_model'),
    url(r'spam_check$', 'apps.core.views.spam_check', name='spam_check'),
    url(r'ajax_get_customer_status$', 'apps.core.views.ajax_get_customer_status', name='ajax_get_customer_status'),
    url(r'ajax_get_smtp_status$', 'apps.core.views.ajax_get_smtp_status', name='ajax_get_smtp_status'),
    url(r'^auditlog$', 'apps.core.views.auditlog', name='auditlog'),
    url(r'^ajax_get_auditlog$', 'apps.core.views.ajax_get_auditlog', name='ajax_get_auditlog'),
    # url(r'notice/(?P<id>\d+)/$', 'apps.core.views.notice', name='notice'),
)
