from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^edm_check_settings$', 'apps.mail.views.edm_check_settings_list', name='edm_check_settings_list'),
    url(r'^edm_check_settings/(?P<id>\d+)/$', 'apps.mail.views.edm_check_settings_modify', name='edm_check_settings_modify'),
    url(r'^edm_check_settings/add/$', 'apps.mail.views.edm_check_settings_add', name='edm_check_settings_add'),
    url(r'^credit_interval_settings$', 'apps.mail.views.credit_interval_settings', name='credit_interval_settings'),
    url(r'^credit_interval_settings/change_status$', 'apps.mail.views.credit_interval_settings_change_status', name='credit_interval_settings_change_status'),
    url(r'^sender_credit_settings$', 'apps.mail.views.sender_credit_settings', name='sender_credit_settings'),
    url(r'^spam_rpt_settings$', 'apps.mail.views.spam_rpt_settings', name='spam_rpt_settings'),
    url(r'^check_settings$', 'apps.mail.views.check_settings', name='check_settings'),
    url(r'^bounce_settings$', 'apps.mail.views.bounce_settings', name='bounce_settings'),
    url(r'^notice_settings$', 'apps.mail.views.notice_settings', name='notice_settings'),
    url(r'^settings$', 'apps.mail.views.settings', name='settings'),
    url(r'^csender_credit_settings$', 'apps.collect_mail.setting.sender_credit_settings', name='csender_credit_settings'),
)

