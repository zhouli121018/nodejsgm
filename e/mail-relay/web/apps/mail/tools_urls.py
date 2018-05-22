from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'mail_reject$', 'apps.mail.views.mail_reject', name='mail_reject'),
                       url(r'operation_doc$', 'apps.mail.views.operation_doc', name='operation_doc'),

)
