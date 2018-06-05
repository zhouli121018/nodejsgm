# -*- coding:utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^p/$', views.perm_list, name='perm_list'),
    url(r'^p/add/$', views.perm_add, name='perm_add'),
    url(r'^p/(?P<perm_id>\d+)/$', views.perm_modify, name='perm_modify'),

    url(r'group/$', views.group_list, name='group_list'),
    url(r'group/(?P<group_id>\d+)/$', views.group_modify, name='group_modify'),
    url(r'group/add/$', views.group_add, name='group_add'),

    url(r'grant/$', views.perm_grant, name='perm_grant'),

    url(r'user/$', views.user_list, name='user_list'),
    url(r'user/add/$', views.user_add, name='user_add'),
    url(r'user/(?P<user_id>\d+)/$', views.user_modify, name='user_modify'),
    url(r'user/passwd/c/(?P<user_id>\d+)/$', views.user_passwd_change, name='user_passwd_change'),
    url(r'user/passwd/s/(?P<user_id>\d+)/$', views.user_passwd_set, name='user_passwd_set'),
]
