from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'mail_list$', 'apps.mail.views.mail_list', name='mail_list'),
    url(r'domain_blacklist$', 'apps.mail.views.domain_blacklist_list', name='domain_blacklist_list'),
    url(r'domain_blacklist/(?P<domain_blacklist_id>\d+)/$', 'apps.mail.views.domain_blacklist_modify', name='domain_blacklist_modify'),
    url(r'domain_blacklist/add/$', 'apps.mail.views.domain_blacklist_add', name='domain_blacklist_add'),
    url(r'domain_blacklist/batch_add/$', 'apps.mail.views.domain_blacklist_batch_add', name='domain_blacklist_batch_add'),

    url(r'custom_keyword_blacklist$', 'apps.mail.views.custom_keyword_blacklist_list', name='custom_keyword_blacklist_list'),
    url(r'custom_keyword_blacklist/(?P<custom_keyword_blacklist_id>\d+)/$', 'apps.mail.views.custom_keyword_blacklist_modify', name='custom_keyword_blacklist_modify'),
    url(r'custom_keyword_blacklist/add/$', 'apps.mail.views.custom_keyword_blacklist_add', name='custom_keyword_blacklist_add'),
    url(r'custom_keyword_blacklist/batch_add/$', 'apps.mail.views.custom_keyword_blacklist_batch_add', name='custom_keyword_blacklist_batch_add'),

    url(r'subject_keyword_blacklist$', 'apps.mail.views.subject_keyword_blacklist_list', name='subject_keyword_blacklist_list'),
    url(r'subject_keyword_blacklist/(?P<subject_keyword_blacklist_id>\d+)/$', 'apps.mail.views.subject_keyword_blacklist_modify', name='subject_keyword_blacklist_modify'),
    url(r'subject_keyword_blacklist/add/$', 'apps.mail.views.subject_keyword_blacklist_add', name='subject_keyword_blacklist_add'),
    url(r'subject_keyword_blacklist/batch_add/$', 'apps.mail.views.subject_keyword_blacklist_batch_add', name='subject_keyword_blacklist_batch_add'),

    url(r'keyword_blacklist$', 'apps.mail.views.keyword_blacklist_list', name='keyword_blacklist_list'),
    url(r'keyword_blacklist/(?P<keyword_blacklist_id>\d+)/$', 'apps.mail.views.keyword_blacklist_modify', name='keyword_blacklist_modify'),
    url(r'keyword_blacklist/add/$', 'apps.mail.views.keyword_blacklist_add', name='keyword_blacklist_add'),
    url(r'keyword_blacklist/batch_add/$', 'apps.mail.views.keyword_blacklist_batch_add', name='keyword_blacklist_batch_add'),

    url(r'subject_keyword_whitelist$', 'apps.mail.views.subject_keyword_whitelist_list', name='subject_keyword_whitelist_list'),
    url(r'subject_keyword_whitelist/(?P<subject_keyword_whitelist_id>\d+)/$', 'apps.mail.views.subject_keyword_whitelist_modify', name='subject_keyword_whitelist_modify'),
    url(r'subject_keyword_whitelist/add/$', 'apps.mail.views.subject_keyword_whitelist_add', name='subject_keyword_whitelist_add'),
    url(r'subject_keyword_whitelist/batch_add/$', 'apps.mail.views.subject_keyword_whitelist_batch_add', name='subject_keyword_whitelist_batch_add'),

    url(r'mail_review$', 'apps.mail.views.mail_review', name='mail_review'),
    url(r'mail_review_undo$', 'apps.mail.views.mail_review_undo', name='mail_review_undo'),
    url(r'mail_read$', 'apps.mail.views.mail_read', name='mail_read'),
    url(r'ajax_get_mails$', 'apps.mail.views.ajax_get_mails', name='ajax_get_mails'),
    url(r'mail_summary$', 'apps.mail.views.mail_summary', name='mail_summary'),
    url(r'check_settings$', 'apps.mail.views.check_settings', name='check_settings'),
    url(r'bounce_settings$', 'apps.mail.views.bounce_settings', name='bounce_settings'),

    url(r'report_spam$', 'apps.mail.views.report_spam', name='report_spam'),
    url(r'mail_recheck$', 'apps.mail.views.mail_recheck', name='mail_recheck'),
    url(r'bulk_list$', 'apps.mail.views.bulk_list', name='bulk_list'),


    url(r'statistics$', 'apps.mail.views.statistics', name='statistics'),

    url(r'sender_blacklist$', 'apps.mail.views.sender_blacklist_list', name='sender_blacklist_list'),
    url(r'sender_blacklist/(?P<sender_blacklist_id>\d+)/$', 'apps.mail.views.sender_blacklist_modify', name='sender_blacklist_modify'),
    url(r'sender_blacklist/add/$', 'apps.mail.views.sender_blacklist_add', name='sender_blacklist_add'),
    url(r'sender_blacklist/batch_add/$', 'apps.mail.views.sender_blacklist_batch_add', name='sender_blacklist_batch_add'),

    url(r'^invalid_mail$', 'apps.mail.views.invalid_mail_list', name='invalid_mail_list'),
    url(r'invalid_mail/(?P<invalid_mail_id>\d+)/$', 'apps.mail.views.invalid_mail_modify', name='invalid_mail_modify'),
    url(r'invalid_mail/add/$', 'apps.mail.views.invalid_mail_add', name='invalid_mail_add'),
    url(r'invalid_mail/batch_add/$', 'apps.mail.views.invalid_mail_batch_add', name='invalid_mail_batch_add'),
    url(r'ajax_get_invalid_mail$', 'apps.mail.views.ajax_get_invalid_mail', name='ajax_get_invalid_mail'),

    url(r'op_keywordlist$', 'apps.mail.views.op_keywordlist', name='op_keywordlist'),

    url(r'recipient_blacklist$', 'apps.mail.views.recipient_blacklist_list', name='recipient_blacklist_list'),
    url(r'recipient_blacklist/(?P<recipient_blacklist_id>\d+)/$', 'apps.mail.views.recipient_blacklist_modify', name='recipient_blacklist_modify'),
    url(r'recipient_blacklist/add/$', 'apps.mail.views.recipient_blacklist_add', name='recipient_blacklist_add'),
    url(r'recipient_blacklist/batch_add/$', 'apps.mail.views.recipient_blacklist_batch_add', name='recipient_blacklist_batch_add'),

    url(r'settings$', 'apps.mail.views.settings', name='settings'),
    url(r'deliver_logs/(?P<id>\w+)/$', 'apps.mail.views.deliver_logs', name='deliver_logs'),
    url(r'spf_error_list$', 'apps.mail.views.spf_error_list', name='spf_error_list'),

    url(r'spam_sender_list$', 'apps.mail.views.spam_sender_list', name='spam_sender_list'),

    url(r'mail_suffix$', 'apps.mail.views.mail_suffix_list', name='mail_suffix_list'),
    url(r'mail_suffix/(?P<mail_suffix_id>\d+)/$', 'apps.mail.views.mail_suffix_modify', name='mail_suffix_modify'),
    url(r'mail_suffix/add/$', 'apps.mail.views.mail_suffix_add', name='mail_suffix_add'),
    url(r'mail_suffix/batch_add/$', 'apps.mail.views.mail_suffix_batch_add', name='mail_suffix_batch_add'),

    url(r'bulk_customer_list$', 'apps.mail.views.bulk_customer_list', name='bulk_customer_list'),

)
