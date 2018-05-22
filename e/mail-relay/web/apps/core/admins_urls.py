from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'mypermission_list$', 'apps.core.admins_views.mypermission_list', name='mypermission_list'),
    url(r'mypermission/(?P<mypermission_id>\d+)/$', 'apps.core.admins_views.mypermission_modify', name='mypermission_modify'),
    url(r'mypermission/add/$$', 'apps.core.admins_views.mypermission_add', name='mypermission_add'),

    url(r'grant_permission$', 'apps.core.admins_views.grant_permission', name='grant_permission'),

    url(r'group_list$', 'apps.core.admins_views.group_list', name='group_list'),
    url(r'group/(?P<group_id>\d+)/$', 'apps.core.admins_views.group_modify', name='group_modify'),
    url(r'group/add/$$', 'apps.core.admins_views.group_add', name='group_add'),

    url(r'user_list$', 'apps.core.admins_views.user_list', name='user_list'),
    url(r'user/(?P<user_id>\d+)/$', 'apps.core.admins_views.user_modify', name='user_modify'),
    url(r'user/(?P<user_id>\d+)/password/$', 'apps.core.admins_views.password_modify', name='password_modify'),
    url(r'user/add/$', 'apps.core.admins_views.user_add', name='user_add'),
    url(r'user/ajax_get_users/$', 'apps.core.admins_views.ajax_get_users', name='ajax_get_users'),

    url(r'operation_doc$', 'apps.mail.views.operation_doc', name='a_operation_doc'),
)