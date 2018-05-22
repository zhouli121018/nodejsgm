from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^ajax_get_subject_blacklist$', 'apps.mail.check_views.ajax_get_subject_blacklist', name='ajax_get_subject_blacklist'),
    url(r'^ajax_get_keyword_blacklist$', 'apps.mail.check_views.ajax_get_keyword_blacklist', name='ajax_get_keyword_blacklist'),
    url(r'^ajax_get_sender_blacklist$', 'apps.mail.check_views.ajax_get_sender_blacklist', name='ajax_get_sender_blacklist'),
    url(r'^ajax_get_attach_blacklist$', 'apps.mail.check_views.ajax_get_attach_blacklist', name='ajax_get_attach_blacklist'),
    url(r'^domain_blacklist$', 'apps.mail.check_views.domain_blacklist_list', name='domain_blacklist_list'),
    url(r'^domain_blacklist/(?P<domain_blacklist_id>\d+)/$', 'apps.mail.check_views.domain_blacklist_modify', name='domain_blacklist_modify'),
    url(r'^domain_blacklist/add/$', 'apps.mail.check_views.domain_blacklist_add', name='domain_blacklist_add'),
    url(r'^domain_blacklist/batch_add/$', 'apps.mail.check_views.domain_blacklist_batch_add', name='domain_blacklist_batch_add'),

    url(r'^custom_keyword_blacklist$', 'apps.mail.check_views.custom_keyword_blacklist_list', name='custom_keyword_blacklist_list'),
    url(r'^custom_keyword_blacklist/(?P<custom_keyword_blacklist_id>\d+)/$', 'apps.mail.check_views.custom_keyword_blacklist_modify', name='custom_keyword_blacklist_modify'),
    url(r'^custom_keyword_blacklist/add/$', 'apps.mail.check_views.custom_keyword_blacklist_add', name='custom_keyword_blacklist_add'),
    url(r'^custom_keyword_blacklist/batch_add/$', 'apps.mail.check_views.custom_keyword_blacklist_batch_add', name='custom_keyword_blacklist_batch_add'),

    url(r'^subject_keyword_blacklist$', 'apps.mail.check_views.subject_keyword_blacklist_list', name='subject_keyword_blacklist_list'),
    url(r'^subject_keyword_blacklist/(?P<subject_keyword_blacklist_id>\d+)/$', 'apps.mail.check_views.subject_keyword_blacklist_modify', name='subject_keyword_blacklist_modify'),
    url(r'^subject_keyword_blacklist/add/$', 'apps.mail.check_views.subject_keyword_blacklist_add', name='subject_keyword_blacklist_add'),
    url(r'^subject_keyword_blacklist/batch_add/$', 'apps.mail.check_views.subject_keyword_blacklist_batch_add', name='subject_keyword_blacklist_batch_add'),

    url(r'^keyword_blacklist$', 'apps.mail.check_views.keyword_blacklist_list', name='keyword_blacklist_list'),
    url(r'^keyword_blacklist/(?P<keyword_blacklist_id>\d+)/$', 'apps.mail.check_views.keyword_blacklist_modify', name='keyword_blacklist_modify'),
    url(r'^keyword_blacklist/add/$', 'apps.mail.check_views.keyword_blacklist_add', name='keyword_blacklist_add'),
    url(r'^keyword_blacklist/batch_add/$', 'apps.mail.check_views.keyword_blacklist_batch_add', name='keyword_blacklist_batch_add'),

    url(r'^subject_keyword_whitelist$', 'apps.mail.check_views.subject_keyword_whitelist_list', name='subject_keyword_whitelist_list'),
    url(r'^subject_keyword_whitelist/(?P<subject_keyword_whitelist_id>\d+)/$', 'apps.mail.check_views.subject_keyword_whitelist_modify', name='subject_keyword_whitelist_modify'),
    url(r'^subject_keyword_whitelist/add/$', 'apps.mail.check_views.subject_keyword_whitelist_add', name='subject_keyword_whitelist_add'),
    url(r'^subject_keyword_whitelist/batch_add/$', 'apps.mail.check_views.subject_keyword_whitelist_batch_add', name='subject_keyword_whitelist_batch_add'),

    url(r'^ajax_get_customer_sender_blacklist$', 'apps.mail.check_views.ajax_get_customer_sender_blacklist', name='ajax_get_customer_sender_blacklist'),

    url(r'^customer_sender_blacklist$', 'apps.mail.check_views.customer_sender_blacklist_list', name='customer_sender_blacklist_list'),
    url(r'^customer_sender_blacklist/(?P<customer_sender_blacklist_id>\d+)/$', 'apps.mail.check_views.customer_sender_blacklist_modify', name='customer_sender_blacklist_modify'),
    url(r'^customer_sender_blacklist/add/$', 'apps.mail.check_views.customer_sender_blacklist_add', name='customer_sender_blacklist_add'),
    url(r'^customer_sender_blacklist/batch_add/$', 'apps.mail.check_views.customer_sender_blacklist_batch_add', name='customer_sender_blacklist_batch_add'),

    url(r'^temp_sender_blacklist$', 'apps.mail.check_views.temp_sender_blacklist_list', name='temp_sender_blacklist_list'),

    url(r'^sender_blacklist$', 'apps.mail.check_views.sender_blacklist_list', name='sender_blacklist_list'),
    url(r'^sender_blacklist/(?P<sender_blacklist_id>\d+)/$', 'apps.mail.check_views.sender_blacklist_modify', name='sender_blacklist_modify'),
    url(r'^sender_blacklist/add/$', 'apps.mail.check_views.sender_blacklist_add', name='sender_blacklist_add'),
    url(r'^sender_blacklist/batch_add/$', 'apps.mail.check_views.sender_blacklist_batch_add', name='sender_blacklist_batch_add'),

    url(r'^invalid_mail$', 'apps.mail.check_views.invalid_mail_list', name='invalid_mail_list'),
    url(r'^invalid_mail/(?P<invalid_mail_id>\d+)/$', 'apps.mail.check_views.invalid_mail_modify', name='invalid_mail_modify'),
    url(r'^invalid_mail/add/$', 'apps.mail.check_views.invalid_mail_add', name='invalid_mail_add'),
    url(r'^invalid_mail/batch_add/$', 'apps.mail.check_views.invalid_mail_batch_add', name='invalid_mail_batch_add'),
    url(r'^ajax_get_invalid_mail$', 'apps.mail.check_views.ajax_get_invalid_mail', name='ajax_get_invalid_mail'),

    url(r'^recipient_blacklist$', 'apps.mail.check_views.recipient_blacklist_list', name='recipient_blacklist_list'),
    url(r'^recipient_blacklist/(?P<recipient_blacklist_id>\d+)/$', 'apps.mail.check_views.recipient_blacklist_modify', name='recipient_blacklist_modify'),
    url(r'^recipient_blacklist/add/$', 'apps.mail.check_views.recipient_blacklist_add', name='recipient_blacklist_add'),
    url(r'^recipient_blacklist/batch_add/$', 'apps.mail.check_views.recipient_blacklist_batch_add', name='recipient_blacklist_batch_add'),

    url(r'^ajax_get_collect_recipient_whitelist$', 'apps.mail.check_views.ajax_get_collect_recipient_whitelist', name='ajax_get_collect_recipient_whitelist'),
    url(r'^collect_recipient_whitelist$', 'apps.mail.check_views.collect_recipient_whitelist_list', name='collect_recipient_whitelist_list'),
    url(r'^collect_recipient_whitelist/(?P<collect_recipient_whitelist_id>\d+)/$', 'apps.mail.check_views.collect_recipient_whitelist_modify', name='collect_recipient_whitelist_modify'),
    url(r'^collect_recipient_whitelist/add/$', 'apps.mail.check_views.collect_recipient_whitelist_add', name='collect_recipient_whitelist_add'),
    url(r'^collect_recipient_whitelist/batch_add/$', 'apps.mail.check_views.collect_recipient_whitelist_batch_add', name='collect_recipient_whitelist_batch_add'),

    url(r'^mail_suffix$', 'apps.mail.check_views.mail_suffix_list', name='mail_suffix_list'),
    url(r'^mail_suffix/(?P<mail_suffix_id>\d+)/$', 'apps.mail.check_views.mail_suffix_modify', name='mail_suffix_modify'),
    url(r'^mail_suffix/add/$', 'apps.mail.check_views.mail_suffix_add', name='mail_suffix_add'),
    url(r'^mail_suffix/batch_add/$', 'apps.mail.check_views.mail_suffix_batch_add', name='mail_suffix_batch_add'),

    url(r'^attachment_blacklist$', 'apps.mail.check_views.attachment_blacklist_list', name='attachment_blacklist_list'),
    url(r'^attachment_blacklist/(?P<attachment_blacklist_id>\d+)/$', 'apps.mail.check_views.attachment_blacklist_modify', name='attachment_blacklist_modify'),
    url(r'^attachment_blacklist/add/$', 'apps.mail.check_views.attachment_blacklist_add', name='attachment_blacklist_add'),
    url(r'^attachment_blacklist/batch_add/$', 'apps.mail.check_views.attachment_blacklist_batch_add', name='attachment_blacklist_batch_add'),

    url(r'^attachment_type_blacklist$', 'apps.mail.check_views.attachment_type_blacklist_list', name='attachment_type_blacklist_list'),
    url(r'^attachment_type_blacklist/(?P<attachment_type_blacklist_id>\d+)/$', 'apps.mail.check_views.attachment_type_blacklist_modify', name='attachment_type_blacklist_modify'),
    url(r'^attachment_type_blacklist/add/$', 'apps.mail.check_views.attachment_type_blacklist_add', name='attachment_type_blacklist_add'),
    url(r'^attachment_type_blacklist/batch_add/$', 'apps.mail.check_views.attachment_type_blacklist_batch_add', name='attachment_type_blacklist_batch_add'),


    url(r'^spam_sender_list$', 'apps.mail.check_views.spam_sender_list', name='spam_sender_list'),
    url(r'^ajax_change_check_list$', 'apps.mail.check_views.ajax_change_check_list', name='ajax_change_check_list'),

    url(r'^ajax_add_sender_whitelist$', 'apps.mail.check_views.ajax_add_sender_whitelist', name='ajax_add_sender_whitelist'),
    url(r'^ajax_add_sender_blacklist$', 'apps.mail.check_views.ajax_add_sender_blacklist', name='ajax_add_sender_blacklist'),

    url(r'^invalidsender_whitelist$', 'apps.mail.check_views.invalidsender_whitelist_list', name='invalidsender_whitelist_list'),
    url(r'^invalidsender_whitelist/(?P<invalidsender_whitelist_id>\d+)/$', 'apps.mail.check_views.invalidsender_whitelist_modify', name='invalidsender_whitelist_modify'),
    url(r'^invalidsender_whitelist/add/$', 'apps.mail.check_views.invalidsender_whitelist_add', name='invalidsender_whitelist_add'),
    url(r'^invalidsender_whitelist/batch_add/$', 'apps.mail.check_views.invalidsender_whitelist_batch_add', name='invalidsender_whitelist_batch_add'),

    url(r'^ajax_get_sender_whitelist$', 'apps.mail.check_views.ajax_get_sender_whitelist', name='ajax_get_sender_whitelist'),

    url(r'^sender_whitelist$', 'apps.mail.check_views.sender_whitelist_list', name='sender_whitelist_list'),
    url(r'^sender_whitelist/(?P<sender_whitelist_id>\d+)/$', 'apps.mail.check_views.sender_whitelist_modify', name='sender_whitelist_modify'),
    url(r'^sender_whitelist/add/$', 'apps.mail.check_views.sender_whitelist_add', name='sender_whitelist_add'),
    url(r'^sender_whitelist/batch_add/$', 'apps.mail.check_views.sender_whitelist_batch_add', name='sender_whitelist_batch_add'),

    url(r'^ajax_get_checklist$', 'apps.mail.check_views.ajax_get_checklist', name='ajax_get_checklist'),
    url(r'^spf_checklist$', 'apps.mail.check_views.spf_checklist_list', name='spf_checklist_list'),
    url(r'^spf_checklist/(?P<spf_checklist_id>\d+)/$', 'apps.mail.check_views.spf_checklist_modify', name='spf_checklist_modify'),
    url(r'^spf_checklist/add/$', 'apps.mail.check_views.spf_checklist_add', name='spf_checklist_add'),
    url(r'^spf_checklist/batch_add/$', 'apps.mail.check_views.spf_checklist_batch_add', name='spf_checklist_batch_add'),

    url(r'^ajax_add_tempsenderblacklist$', 'apps.mail.check_views.ajax_add_tempsenderblacklist', name='ajax_add_tempsenderblacklist'),

    url(r'^ajax_get_recipient_whitelist$', 'apps.mail.check_views.ajax_get_recipient_whitelist', name='ajax_get_recipient_whitelist'),
    url(r'^recipient_whitelist$', 'apps.mail.check_views.recipient_whitelist_list', name='recipient_whitelist_list'),
    url(r'^recipient_whitelist/(?P<recipient_whitelist_id>\d+)/$', 'apps.mail.check_views.recipient_whitelist_modify', name='recipient_whitelist_modify'),
    url(r'^recipient_whitelist/add/$', 'apps.mail.check_views.recipient_whitelist_add', name='recipient_whitelist_add'),
    url(r'^recipient_whitelist/batch_add/$', 'apps.mail.check_views.recipient_whitelist_batch_add', name='recipient_whitelist_batch_add'),

    url(r'^ajax_get_relay_sender_whitelist_list$', 'apps.mail.check_views.ajax_get_relay_sender_whitelist_list', name='ajax_get_relay_sender_whitelist_list'),
    url(r'^relay_sender_whitelist_list$', 'apps.mail.check_views.relay_sender_whitelist_list', name='relay_sender_whitelist_list'),
    url(r'^relay_sender_whitelist_list/(?P<sender_whitelist_id>\d+)/$', 'apps.mail.check_views.relay_sender_whitelist_modify', name='relay_sender_whitelist_modify'),
    url(r'^relay_sender_whitelist_list/add/$', 'apps.mail.check_views.relay_sender_whitelist_add', name='relay_sender_whitelist_add'),
    url(r'^relay_sender_whitelist_list/batch_add/$', 'apps.mail.check_views.relay_sender_whitelist_batch_add', name='relay_sender_whitelist_batch_add'),

    url(r'^ajax_get_spam_rpt_blacklist$', 'apps.mail.check_views.ajax_get_spam_rpt_blacklist', name='ajax_get_spam_rpt_blacklist'),
    url(r'^spam_rpt_blacklist$', 'apps.mail.check_views.spam_rpt_blacklist_list', name='spam_rpt_blacklist_list'),
    url(r'^spam_rpt_blacklist/(?P<spam_rpt_blacklist_id>\d+)/$', 'apps.mail.check_views.spam_rpt_blacklist_modify', name='spam_rpt_blacklist_modify'),
    url(r'^spam_rpt_blacklist/add/$', 'apps.mail.check_views.spam_rpt_blacklist_add', name='spam_rpt_blacklist_add'),
    url(r'^spam_rpt_blacklist/batch_add/$', 'apps.mail.check_views.spam_rpt_blacklist_batch_add', name='spam_rpt_blacklist_batch_add'),

    url(r'^ajax_get_collect_recipient_checklist$', 'apps.mail.check_views.ajax_get_collect_recipient_checklist', name='ajax_get_collect_recipient_checklist'),
    url(r'^collect_recipient_checklist$', 'apps.mail.check_views.collect_recipient_checklist_list', name='collect_recipient_checklist_list'),
    url(r'^collect_recipient_checklist/(?P<id>\d+)/$', 'apps.mail.check_views.collect_recipient_checklist_modify', name='collect_recipient_checklist_modify'),
    url(r'^collect_recipient_checklist/add/$', 'apps.mail.check_views.collect_recipient_checklist_add', name='collect_recipient_checklist_add'),
    url(r'^collect_recipient_checklist/batch_add/$', 'apps.mail.check_views.collect_recipient_checklist_batch_add', name='collect_recipient_checklist_batch_add'),

    url(r'^ajax_get_spf_ip_whitelist$', 'apps.mail.check_views.ajax_get_spf_ip_whitelist', name='ajax_get_spf_ip_whitelist'),
    url(r'^spf_ip_whitelist_list$', 'apps.mail.check_views.spf_ip_whitelist_list', name='spf_ip_whitelist_list'),
    url(r'^spf_ip_whitelist_list/(?P<sender_whitelist_id>\d+)/$', 'apps.mail.check_views.spf_ip_whitelist_modify', name='spf_ip_whitelist_modify'),
    url(r'^spf_ip_whitelist_list/add/$', 'apps.mail.check_views.spf_ip_whitelist_add', name='spf_ip_whitelist_add'),
    url(r'^spf_ip_whitelist_list/batch_add/$', 'apps.mail.check_views.spf_ip_whitelist_batch_add', name='spf_ip_whitelist_batch_add'),
)
