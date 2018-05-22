from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'customer_list$', 'apps.collect.views.customer_list', name='col_customer_list'),
    url(r'customer_add$', 'apps.collect.views.customer_add', name='col_customer_add'),
    url(r'customer/(?P<customer_id>\d+)/$', 'apps.collect.views.customer_modify', name='col_customer_modify'),
    url(r'customer/domain/(?P<customer_id>\d+)/$', 'apps.collect.views.customer_domain', name='col_customer_domain'),
    url(r'customer/domain_batchadd/(?P<customer_id>\d+)/$', 'apps.collect.views.customer_domain_batchadd', name='col_customer_domain_batchadd'),
    url(r'customer/domain/(?P<customer_id>\d+)/change_status/$', 'apps.collect.views.customer_domain_change_status', name='col_customer_domain_change_status'),
    url(r'customer_setting/(?P<customer_id>\d+)/$', 'apps.collect.views.customer_setting', name='col_customer_setting'),
    url(r'ajax_get_customers$', 'apps.collect.views.ajax_get_customers', name='ajax_get_col_customers'),
    )