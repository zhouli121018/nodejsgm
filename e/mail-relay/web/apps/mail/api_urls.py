from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'mail_status/$', 'apps.mail.api_views.mail_search_status', name='mail_search_status'),
)
