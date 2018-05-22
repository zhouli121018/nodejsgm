from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^customer_modify/$', 'apps.core.views.customer_modify', name='customer_modify'),
    url(r'^customer_modify/password/$', 'apps.core.views.customer_password_modify', name='customer_password_modify'),
    url(r'^notice_list/$', 'apps.core.views.notice_list', name='notice_list'),
    url(r'^ajax_get_notices$', 'apps.core.views.ajax_get_notices', name='ajax_get_notices'),

    url(r'^operate_log/$', 'apps.core.views.operate_log', name='operate_log'),
    url(r'^ajax_operate_log/$', 'apps.core.views.ajax_operate_log', name='ajax_operate_log'),
)