from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'mail_list$', 'apps.localized_mail.views.mail_list', name='localized_mail_list'),
    #
    url(r'mail_read$', 'apps.localized_mail.views.mail_read', name='localized_mail_read'),
    url(r'ajax_get_mails$', 'apps.localized_mail.views.ajax_get_mails', name='ajax_get_localized_mails'),
    url(r'mail_summary$', 'apps.localized_mail.views.mail_summary', name='localized_mail_summary'),
)
