from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'mail_list$', 'apps.mail.views.mail_list', name='mail_list'),

    url(r'mail_read$', 'apps.mail.views.mail_read', name='mail_read'),
    url(r'send_mail_file$', 'apps.mail.views.send_mail_file', name='send_mail_file'),
    url(r'ajax_get_mails$', 'apps.mail.views.ajax_get_mails', name='ajax_get_mails'),
    url(r'mail_summary$', 'apps.mail.views.mail_summary', name='mail_summary'),

    url(r'report_spam$', 'apps.mail.views.report_spam', name='report_spam'),
    url(r'forbiden_rcpt_white$', 'apps.mail.views.forbiden_rcpt_white', name='forbiden_rcpt_white'),
    url(r'mail_recheck$', 'apps.mail.views.mail_recheck', name='mail_recheck'),
    url(r'bulk_list$', 'apps.mail.views.bulk_list', name='bulk_list'),
    url(r'^add_relay_sender_whitelist$', 'apps.mail.views.add_relay_sender_whitelist', name='add_relay_sender_whitelist'),


    url(r'review_statistics$', 'apps.mail.views.review_statistics', name='review_statistics'),
    url(r'check_statistics$', 'apps.mail.views.check_statistics', name='check_statistics'),
    url(r'statistics$', 'apps.mail.views.statistics', name='statistics'),

    url(r'op_keywordlist$', 'apps.mail.views.op_keywordlist', name='op_keywordlist'),

    url(r'deliver_logs/(?P<id>\w+)/$', 'apps.mail.views.deliver_logs', name='deliver_logs'),
    url(r'spf_error_list$', 'apps.mail.views.spf_error_list', name='spf_error_list'),
    url(r'spf_error/(?P<id>\d+)/$', 'apps.mail.views.spf_error_modify', name='spf_error_modify'),

    url(r'bulk_customer_list$', 'apps.mail.views.bulk_customer_list', name='bulk_customer_list'),

    url(r'state_logs/(?P<id>\w+)/$', 'apps.mail.views.state_logs', name='state_logs'),

    url(r'ajax_add_tmp_sender_blacklist$', 'apps.mail.views.ajax_add_tmp_sender_blacklist', name='ajax_add_tmp_sender_blacklist'),

    url(r'^ajax_get_sender_blocked_record_log$', 'apps.mail.check_views.ajax_get_sender_blocked_record_log', name='ajax_get_sender_blocked_record_log'),
    url(r'^sender_blocked_record_log$', 'apps.mail.check_views.sender_blocked_record_log', name='sender_blocked_record_log'),

    url(r'^ajax_get_sender_credit$', 'apps.mail.views.ajax_get_sender_credit', name='ajax_get_sender_credit'),
    url(r'^sender_credit$', 'apps.mail.views.sender_credit', name='sender_credit'),
    url(r'^sender_credit/(?P<sender_credit_id>\d+)/$', 'apps.mail.views.sender_credit_modify', name='sender_credit_modify'),

    url(r'^ajax_update_sender_credit$', 'apps.mail.views.ajax_update_sender_credit', name='ajax_update_sender_credit'),

    url(r'^ajax_get_sender_credit_log$', 'apps.mail.views.ajax_get_sender_credit_log', name='ajax_get_sender_credit_log'),
    url(r'^sender_credit_log$', 'apps.mail.views.sender_credit_log', name='sender_credit_log'),
    url(r'^sender_warning$', 'apps.mail.views.sender_warning', name='sender_warning'),

    url(r'^active_sender_list$', 'apps.mail.views.active_sender_list', name='active_sender_list'),
)
