# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^account$', views.account, name='mailbox_account'),
    url(r'^add_account$', views.add_account, name='mailbox_add_account'),
    url(r'^edit_account/(?P<id>\d+)/$', views.edit_account, name='mailbox_edit_account'),
    url(r'^batchadd_account$', views.batchadd_account, name='mailbox_batchadd_account'),
    url(r'^batchedit_account$', views.batchedit_account, name='mailbox_batchedit_account'),
    url(r'^delete_account$', views.delete_account, name='mailbox_delete_account'),
    url(r'^backup_account$', views.backup_account, name='mailbox_backup_account'),
    url(r'^ajax_get_account$', views.ajax_get_account, name='mailbox_ajax_get_account'),
    url(r'^reply/(?P<id>\d+)/$', views.reply, name='mailbox_reply'),
    url(r'^forward/(?P<id>\d+)/$', views.forward, name='mailbox_forward'),
]