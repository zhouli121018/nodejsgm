from django.conf.urls import url

urlpatterns = [
    url(r'^mail_list$', 'apps.collect_mail.views.mail_list', name='c_mail_list'),
    url(r'^ajax_get_mails$', 'apps.collect_mail.views.ajax_get_mails', name='c_ajax_get_mails'),
    url(r'^mail_read$', 'apps.collect_mail.views.mail_read', name='c_mail_read'),
    url(r'^mail_review$', 'apps.collect_mail.views.mail_review', name='c_mail_review'),
    url(r'^deliver_logs/(?P<id>\w+)/$', 'apps.collect_mail.views.deliver_logs', name='c_deliver_logs'),
    url(r'^mail_summary$', 'apps.collect_mail.views.mail_summary', name='c_mail_summary'),
    url(r'^customer_report$', 'apps.collect_mail.views.customer_report', name='c_mail_customer_report'),

    url(r'^ajax_add_sender_whitelist$', 'apps.collect_mail.views.ajax_add_sender_whitelist', name='ajax_add_sender_whitelist'),
    url(r'^ajax_add_sender_blacklist$', 'apps.collect_mail.views.ajax_add_sender_blacklist', name='ajax_add_sender_blacklist'),
    url(r'^sender_whitelist$', 'apps.collect_mail.views.sender_whitelist_list', name='sender_whitelist_list'),
    url(r'^sender_whitelist/(?P<sender_whitelist_id>\d+)/$', 'apps.collect_mail.views.sender_whitelist_modify', name='sender_whitelist_modify'),
    url(r'^sender_whitelist/add/$', 'apps.collect_mail.views.sender_whitelist_add', name='sender_whitelist_add'),

    # url(r'ajax_add_recipient_whitelist$', 'apps.collect_mail.views.ajax_add_recipient_whitelist', name='ajax_add_recipient_whitelist'),
    url(r'^recipient_whitelist$', 'apps.collect_mail.views.recipient_whitelist_list', name='recipient_whitelist_list'),
    url(r'^recipient_whitelist/(?P<recipient_whitelist_id>\d+)/$', 'apps.collect_mail.views.recipient_whitelist_modify', name='recipient_whitelist_modify'),
    url(r'^recipient_whitelist/add/$', 'apps.collect_mail.views.recipient_whitelist_add', name='recipient_whitelist_add'),

    url(r'^sender_blacklist$', 'apps.collect_mail.views.sender_blacklist_list', name='sender_blacklist_list'),
    url(r'^sender_blacklist/(?P<sender_blacklist_id>\d+)/$', 'apps.collect_mail.views.sender_blacklist_modify', name='sender_blacklist_modify'),
    url(r'^sender_blacklist/add/$', 'apps.collect_mail.views.sender_blacklist_add', name='sender_blacklist_add'),

    url(r'^setting$', 'apps.collect_mail.views.setting', name='c_mail_setting'),
    url(r'^statistics$', 'apps.collect_mail.views.statistics', name='c_mail_statistics'),
    url(r'resent$', 'apps.collect_mail.views.resent', name='collect_resent'),
    url(r'^active_receiver_list$', 'apps.collect_mail.views.active_receiver_list', name='active_receiver_list'),

    url(r'^spam_rpt_blacklist$', 'apps.collect_mail.views.spam_rpt_blacklist_list', name='spam_rpt_blacklist_list'),
    url(r'^spam_rpt_blacklist/(?P<spam_rpt_blacklist_id>\d+)/$', 'apps.collect_mail.views.spam_rpt_blacklist_modify', name='spam_rpt_blacklist_modify'),
    url(r'^spam_rpt_blacklist/add/$', 'apps.collect_mail.views.spam_rpt_blacklist_add', name='spam_rpt_blacklist_add'),
]
