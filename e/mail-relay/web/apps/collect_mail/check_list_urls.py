from django.conf.urls import patterns, url

urlpatterns = patterns('',

    url(r'subject_keyword_blacklist$', 'apps.collect_mail.views.subject_keyword_blacklist_list', name='c_subject_keyword_blacklist_list'),
    url(r'subject_keyword_blacklist/(?P<subject_keyword_blacklist_id>\d+)/$', 'apps.collect_mail.views.subject_keyword_blacklist_modify', name='c_subject_keyword_blacklist_modify'),
    url(r'subject_keyword_blacklist/add/$', 'apps.collect_mail.views.subject_keyword_blacklist_add', name='c_subject_keyword_blacklist_add'),
    url(r'subject_keyword_blacklist/batch_add/$', 'apps.collect_mail.views.subject_keyword_blacklist_batch_add', name='c_subject_keyword_blacklist_batch_add'),

    url(r'keyword_blacklist$', 'apps.collect_mail.views.keyword_blacklist_list', name='c_keyword_blacklist_list'),
    url(r'keyword_blacklist/(?P<keyword_blacklist_id>\d+)/$', 'apps.collect_mail.views.keyword_blacklist_modify', name='c_keyword_blacklist_modify'),
    url(r'keyword_blacklist/add/$', 'apps.collect_mail.views.keyword_blacklist_add', name='c_keyword_blacklist_add'),
    url(r'keyword_blacklist/batch_add/$', 'apps.collect_mail.views.keyword_blacklist_batch_add', name='c_keyword_blacklist_batch_add'),

    url(r'high_risk_flag$', 'apps.collect_mail.views.high_risk_flag_list', name='c_high_risk_flag_list'),
    url(r'high_risk_flag/(?P<high_risk_flag_id>\d+)/$', 'apps.collect_mail.views.high_risk_flag_modify', name='c_high_risk_flag_modify'),
    url(r'high_risk_flag/add/$$', 'apps.collect_mail.views.high_risk_flag_add', name='c_high_risk_flag_add'),
    url(r'high_risk_flag/batch_add/$$', 'apps.collect_mail.views.high_risk_flag_batch_add', name='c_high_risk_flag_batch_add'),

)
