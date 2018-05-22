from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^domain/$', views.send_domain, name='send_domain'),
    url(r'^mailbox/add/$', views.core_mailbox_add, name='core_mailbox_add'),
    url(r'^mailbox/add/ajaxpasswd/$', views.ajax_check_mailbox, name='ajax_check_mailbox'),
    url(r'^ajax_core_mailbox/$', views.ajax_core_mailbox, name='ajax_core_mailbox'),
    url(r'^ajax_check_domain/$', views.ajax_check_domain, name='ajax_check_domain'),

    url(r'^track/add/$', views.track_domain_add, name='track_domain_add'),
    url(r'^track/add/check/$', views.ajax_track_domain_add_check, name='ajax_track_domain_add_check'),
    url(r'^tag_customer/$', views.tag_customer, name='tag_customer'),
    url(r'^tagging_open_three/$', views.tagging_open_three, name='tagging_open_three'),
    url(r'^mail_accurate_service_open_three/$', views.mail_accurate_service_open_three, name='mail_accurate_service_open_three'),
    url(r'^ajax_tag_search/$', views.ajax_tag_search, name='ajax_tag_search'),


    url(r'^ml_tag/$', views.ml_maillist_batch_tag, name='ml_maillist_batch_tag'),
]

