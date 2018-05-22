from django.conf.urls import patterns, url

urlpatterns = patterns('',

    url(r'not_exist_flag$', 'apps.flag.views.not_exist_flag_list', name='not_exist_flag_list'),
    url(r'not_exist_flag/(?P<not_exist_flag_id>\d+)/$', 'apps.flag.views.not_exist_flag_modify', name='not_exist_flag_modify'),
    url(r'not_exist_flag/add/$$', 'apps.flag.views.not_exist_flag_add', name='not_exist_flag_add'),
    url(r'not_exist_flag/batch_add/$$', 'apps.flag.views.not_exist_flag_batch_add', name='not_exist_flag_batch_add'),

    url(r'big_quota_flag$', 'apps.flag.views.big_quota_flag_list', name='big_quota_flag_list'),
    url(r'big_quota_flag/(?P<big_quota_flag_id>\d+)/$', 'apps.flag.views.big_quota_flag_modify', name='big_quota_flag_modify'),
    url(r'big_quota_flag/add/$$', 'apps.flag.views.big_quota_flag_add', name='big_quota_flag_add'),
    url(r'big_quota_flag/batch_add/$$', 'apps.flag.views.big_quota_flag_batch_add', name='big_quota_flag_batch_add'),

    url(r'spam_flag$', 'apps.flag.views.spam_flag_list', name='spam_flag_list'),
    url(r'spam_flag/(?P<spam_flag_id>\d+)/$', 'apps.flag.views.spam_flag_modify', name='spam_flag_modify'),
    url(r'spam_flag/add/$$', 'apps.flag.views.spam_flag_add', name='spam_flag_add'),
    url(r'spam_flag/batch_add/$$', 'apps.flag.views.spam_flag_batch_add', name='spam_flag_batch_add'),

    url(r'not_retry_flag$', 'apps.flag.views.not_retry_flag_list', name='not_retry_flag_list'),
    url(r'not_retry_flag/(?P<not_retry_flag_id>\d+)/$', 'apps.flag.views.not_retry_flag_modify', name='not_retry_flag_modify'),
    url(r'not_retry_flag/add/$$', 'apps.flag.views.not_retry_flag_add', name='not_retry_flag_add'),
    url(r'not_retry_flag/batch_add/$$', 'apps.flag.views.not_retry_flag_batch_add', name='not_retry_flag_batch_add'),

    url(r'spf_flag$', 'apps.flag.views.spf_flag_list', name='spf_flag_list'),
    url(r'spf_flag/(?P<spf_flag_id>\d+)/$', 'apps.flag.views.spf_flag_modify', name='spf_flag_modify'),
    url(r'spf_flag/add/$$', 'apps.flag.views.spf_flag_add', name='spf_flag_add'),
    url(r'spf_flag/batch_add/$$', 'apps.flag.views.spf_flag_batch_add', name='spf_flag_batch_add'),
    url(r'high_risk_flag$', 'apps.flag.views.high_risk_flag_list', name='high_risk_flag_list'),
    url(r'high_risk_flag/(?P<high_risk_flag_id>\d+)/$', 'apps.flag.views.high_risk_flag_modify', name='high_risk_flag_modify'),
    url(r'high_risk_flag/add/$$', 'apps.flag.views.high_risk_flag_add', name='high_risk_flag_add'),
    url(r'high_risk_flag/batch_add/$$', 'apps.flag.views.high_risk_flag_batch_add', name='high_risk_flag_batch_add'),
    url(r'greylist_flag$', 'apps.flag.views.greylist_flag_list', name='greylist_flag_list'),
    url(r'greylist_flag/(?P<greylist_flag_id>\d+)/$', 'apps.flag.views.greylist_flag_modify', name='greylist_flag_modify'),
    url(r'greylist_flag/add/$$', 'apps.flag.views.greylist_flag_add', name='greylist_flag_add'),
    url(r'greylist_flag/batch_add/$$', 'apps.flag.views.greylist_flag_batch_add', name='greylist_flag_batch_add'),
)
