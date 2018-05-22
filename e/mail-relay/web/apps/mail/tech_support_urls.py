from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'bulk_list$', 'apps.mail.views.bulk_list', name='bulk_list'),
    url(r'spf_error_list$', 'apps.mail.views.spf_error_list', name='spf_error_list'),
    url(r'bulk_customer/(?P<id>\d+)/$', 'apps.mail.views.bulk_customer_modify', name='bulk_customer_modify'),
    url(r'bulk_customer$', 'apps.mail.views.bulk_customer', name='bulk_customer'),
    url(r'ajax_get_bulk_sender$', 'apps.mail.views.ajax_get_bulk_sender', name='ajax_get_bulk_sender'),
    url(r'get_bulk_sender$', 'apps.mail.views.get_bulk_sender', name='get_bulk_sender'),
    url(r'bulk_sample$', 'apps.mail.views.mail_list', {'template_name': 'mail/bulk_sample.html'}, name='bulk_sample'),
)
