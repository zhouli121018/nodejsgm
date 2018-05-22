from django.conf.urls import url

urlpatterns = [
    url(r'^dowload_mail_attachment$', 'apps.mail.views.dowload_mail_attachment', name='dowload_mail_attachment'),
    url(r'^dowload_mail_real_attachment$', 'apps.mail.views.dowload_mail_real_attachment', name='dowload_mail_real_attachment'),
    url(r'^mail_list$', 'apps.mail.views.mail_list', name='mail_list'),
    url(r'^mail_summary$', 'apps.mail.views.mail_summary', name='mail_summary'),
    url(r'^ajax_get_mails$', 'apps.mail.views.ajax_get_mails', name='ajax_get_mails'),
    url(r'^mail_read$', 'apps.mail.views.mail_read', name='mail_read'),
    url(r'^mail_review$', 'apps.mail.views.mail_review', name='mail_review'),
    url(r'deliver_logs/(?P<id>\w+)/$', 'apps.mail.views.deliver_logs', name='deliver_logs'),
    url(r'^active_sender_list$', 'apps.mail.views.active_sender_list', name='active_sender_list'),
    url(r'^customer_report$', 'apps.mail.views.customer_report', name='mail_customer_report'),
    url(r'^setting$', 'apps.mail.views.setting', name='mail_setting'),
    url(r'^statistics$', 'apps.mail.views.statistics', name='mail_statistics'),
    url(r'^invalid_address/$', 'apps.mail.views.invalid_address', name='invalid_address'),
    url(r'^invalid_address/ajax_delete$', 'apps.mail.views.ajax_delete_invalid_address', name='ajax_delete_invalid_address'),
    url(r'resent$', 'apps.mail.views.resent', name='resent'),
]
