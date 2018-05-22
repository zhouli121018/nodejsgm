from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'mail_list$', 'apps.collect_mail.views.mail_list', name='collect_mail_list'),

    url(r'mail_read$', 'apps.collect_mail.views.mail_read', name='collect_mail_read'),
    url(r'send_mail_file$', 'apps.collect_mail.views.send_mail_file', name='collect_send_mail_file'),
    url(r'ajax_get_mails$', 'apps.collect_mail.views.ajax_get_mails', name='ajax_get_collect_mails'),
    url(r'mail_summary$', 'apps.collect_mail.views.mail_summary', name='collect_mail_summary'),
    # url(r'check_settings$', 'apps.mail.views.check_settings', name='check_settings'),
    #
    url(r'report_spam$', 'apps.collect_mail.views.report_spam', name='collect_report_spam'),
    url(r'mail_recheck$', 'apps.collect_mail.views.mail_recheck', name='collect_mail_recheck'),
    #
    #
    url(r'review_statistics$', 'apps.collect_mail.views.review_statistics', name='collect_review_statistics'),
    url(r'check_statistics$', 'apps.collect_mail.views.check_statistics', name='collect_check_statistics'),
    url(r'statistics$', 'apps.collect_mail.views.statistics', name='collect_statistics'),
    #
    #
    url(r'op_keywordlist$', 'apps.collect_mail.views.op_keywordlist', name='collect_op_keywordlist'),
    #
    # url(r'settings$', 'apps.mail.views.settings', name='settings'),
    url(r'deliver_logs/(?P<id>\w+)/$', 'apps.collect_mail.views.deliver_logs', name='collect_deliver_logs'),

    url(r'state_logs/(?P<id>\w+)/$', 'apps.collect_mail.views.state_logs', name='collect_state_logs'),
    url(r'resent$', 'apps.collect_mail.views.resent', name='collect_resent'),
    url(r'^active_receiver_list$', 'apps.collect_mail.views.active_receiver_list', name='active_receiver_list'),

    url(r'^ajax_get_sender_credit$', 'apps.collect_mail.setting.ajax_get_sender_credit', name='ajax_get_csender_credit'),
    url(r'^sender_credit$', 'apps.collect_mail.setting.sender_credit', name='csender_credit'),
    url(r'^sender_credit/(?P<sender_credit_id>\d+)/$', 'apps.collect_mail.setting.sender_credit_modify', name='csender_credit_modify'),

    url(r'^ajax_update_sender_credit$', 'apps.collect_mail.setting.ajax_update_sender_credit', name='ajax_update_csender_credit'),

    url(r'^ajax_get_sender_credit_log$', 'apps.collect_mail.setting.ajax_get_sender_credit_log', name='ajax_get_csender_credit_log'),
    url(r'^sender_credit_log$', 'apps.collect_mail.setting.sender_credit_log', name='csender_credit_log'),

)
