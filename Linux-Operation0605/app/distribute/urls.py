# -*- coding: utf-8 -*-

from django.conf.urls import url
from app.distribute import views

urlpatterns = [
    # url(r'^$', views.distribute_list, name='distribute_list'),
    # url(r'^ajax$', views.ajax_distribute_list, name='ajax_distribute_list'),
    # url(r'^add$', views.distribute_add, name='distribute_add'),
    # url(r'^mdf/(?P<proxy_id>\d+)/$', views.distribute_modify, name='distribute_modify'),
    #
    # url(r'^config$', views.config, name='proxy_open_config'),
    #
    # url(r'^status$', views.distribute_server_status, name='distribute_server_status'),
    #
    # url(r'^move$', views.distribute_account_move, name='distribute_account_move'),
    # url(r'^move/ajax$', views.ajax_distribute_move, name='ajax_distribute_move'),
    # url(r'^move/add$', views.distribute_move_add, name='distribute_move_add'),
    # url(r'^move/mdf/(?P<move_id>\d+)/$', views.distribute_move_modify, name='distribute_move_modify'),
]