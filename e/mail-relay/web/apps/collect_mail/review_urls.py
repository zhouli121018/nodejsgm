from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'mail_review$', 'apps.collect_mail.views.mail_review', name='collect_mail_review'),
    url(r'mail_review_undo$', 'apps.collect_mail.views.mail_review_undo', name='collect_mail_review_undo'),
    url(r'op_keywordlist$', 'apps.collect_mail.views.op_keywordlist', name='collect_op_keywordlist'),
    url(r'mail_modify_spam$', 'apps.collect_mail.views.mail_modify_spam', name='mail_modify_spam'),
)
