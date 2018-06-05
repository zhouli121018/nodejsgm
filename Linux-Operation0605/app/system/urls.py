# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^licence$', views.licence, name='system_licence'),
    url(r'^sysinfo$', views.sysinfo, name='system_sysinfo'),
    url(r'^changlog$', views.changlog, name='system_changelog'),
    url(r'^visitlog$', views.visitlog, name='system_visitlog'),
    url(r'^ajax_get_visitlog$', views.ajax_get_visitlog, name='ajax_get_visitlog'),
    url(r'^authlog$', views.authlog, name='system_authlog'),
    url(r'^ajax_get_authlog$', views.ajax_get_authlog, name='ajax_get_authlog'),
]