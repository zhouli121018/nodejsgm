# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^dpt/ch/$', views.choose_department_list, name='choose_department_list'),
    url(r'^mbox/ch/$', views.choose_mailbox_list, name='choose_mailbox_list'),
]
