from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'check_settings$', 'apps.collect_mail.views.check_settings', name='collect_check_settings'),
    url(r'settings$', 'apps.collect_mail.views.settings', name='collect_settings'),
)
