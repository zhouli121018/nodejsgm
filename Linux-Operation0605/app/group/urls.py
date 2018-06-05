# -*- coding:utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.groups, name='core_group_list'),
    url(r'^add/$', views.groups_add, name='core_group_add'),
    url(r'^(?P<group_id>\d+)/$', views.groups_modify, name='core_group_modify'),
    url(r'^mem/(?P<group_id>\d+)/$', views.groups_mem, name='core_group_member'),
    url(r'^mem/ajax/(?P<group_id>\d+)/$', views.groups_mem_ajax, name='core_group_member_ajax'),
    url(r'^add/(?P<group_id>\d+)/$', views.groups_mem_add, name='core_group_member_add'),
]
