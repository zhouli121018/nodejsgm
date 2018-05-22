from django.conf.urls import patterns, url

urlpatterns = patterns('',

    url(r'mail_review$', 'apps.mail.views.mail_review', name='mail_review'),
    url(r'mail_review_undo$', 'apps.mail.views.mail_review_undo', name='mail_review_undo'),
    )

