from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.ml_maillist, name='ml_maillist'),
    url(r'^ajax_ml_maillist/$', views.ajax_ml_maillist, name='ajax_ml_maillist'),
    url(r'^ajax_count/(?P<list_id>\d+)/$', views.ajax_maillist_count, name='ajax_maillist_count'),

    url(r'^add/$', views.ml_maillist_add, name='ml_maillist_add'),
    url(r'^modify/(?P<list_id>\d+)/$', views.ml_maillist_modify, name='ml_maillist_modify'),
    url(r'^maintain/(?P<list_id>\d+)/$', views.ml_maillist_maintain_address, name='ml_maillist_maintain_address'),
    url(r'^ajax_add_address/(?P<list_id>\d+)/$', views.ajax_add_address, name='ajax_add_address'),
    url(r'^upload/$', views.ml_maillist_upload, name='ml_maillist_upload'),
    url(r'^import/log/$', views.ml_import_log, name='ml_import_log'),
    url(r'^import/log/ajax/$', views.ajax_ml_import_log, name='ajax_ml_import_log'),
    url(r'^invalid/(?P<log_id>\d+)/$', views.invalid_view, name='import_invalid_view'),

    url(r'^mul_upld/(?P<list_id>\d+)/$', views.ml_addr_multi_upload, name='ml_addr_multi_upload'),

    url(r'^subscribe/(?P<list_id>\d+)/$', views.ml_subscribe_list, name='ml_subscribe_list'),
    url(r'^ajax_subscribe_list/(?P<list_id>\d+)/$', views.ajax_subscribe_list, name='ajax_subscribe_list'),
    url(r'^subscribe/modify/(?P<list_id>\d+)/(?P<address_id>\d+)/$', views.ml_subscribe_modify, name='ml_subscribe_modify'),
     url(r'^ajax_domain_content/(?P<list_id>\d+)/$', views.ajax_domain_content, name='ajax_domain_content'),

    url(r'^unsubscribe/(?P<list_id>\d+)/$', views.ml_unsubscribe_list, name='ml_unsubscribe_list'),
    url(r'^ajax_unsubscribe_list/(?P<list_id>\d+)/$', views.ajax_unsubscribe_list, name='ajax_unsubscribe_list'),

    url(r'^subscribe/add/$', views.add_subscribe_rec, name='add_subscribe_rec'),
    url(r'^ajax_add_subscriber/$', views.ajax_add_subscriber, name='ajax_add_subscriber'),

    url(r'^export_template_format/$', views.export_template_format, name='export_template_format'),
    url(r'^export_address/(?P<list_id>\d+)/$', views.export_address, name='export_address'),
    url(r'^export_limit/(?P<user_id>\d+)/(?P<list_id>\d+)/$', views.ajax_export_limit, name='ajax_export_limit'),
]