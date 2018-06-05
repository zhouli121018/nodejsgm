# -*- coding:utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.maillist_list, name='maillist_list'),
    url(r'^add/$', views.maillist_add, name='maillist_add'),
    url(r'^(?P<list_id>\d+)/$', views.maillist_modify, name='maillist_modify'),
    url(r'^exp/$', views.maillist_export, name='maillist_export'),
    url(r'^tpl/$', views.maillist_template, name='maillist_template'),
    url(r'^import/$', views.maillist_import, name='maillist_import'),
    url(r'^mt/(?P<list_id>\d+)/$', views.maillist_maintain, name='maillist_maintain'),
    url(r'^mt/ajax/(?P<list_id>\d+)/$', views.maillist_maintain_ajax, name='maillist_maintain_ajax'),
    url(r'^mt/add/(?P<list_id>\d+)/$', views.maillist_maintain_add, name='maillist_maintain_add'),
    url(r'^mt/mf/(?P<list_id>\d+)/(?P<member_id>\d+)/$', views.maillist_maintain_modify, name='maillist_maintain_modify'),
    url(r'^mt/badd/(?P<list_id>\d+)/$', views.maillist_maintain_batchadd, name='maillist_maintain_batchadd'),
    url(r'^mt/select/$', views.maillist_maintain_select, name='maillist_maintain_select'),
    url(r'^mt/select/ajax/$', views.maillist_maintain_select_ajax, name='maillist_maintain_select_ajax'),
    url(r'^mt/exp/(?P<list_id>\d+)/$', views.maillist_maintain_export, name='maillist_maintain_export'),
]
