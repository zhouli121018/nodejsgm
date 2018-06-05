# -*- coding: utf-8 -*-
"""
系统状态url
"""

from django.conf.urls import url
from app.system import views

urlpatterns = [
    url(r'^system/licence$', views.licence, name='system_licence'),
    url(r'^system/sysinfo$', views.sysinfo, name='system_sysinfo'),
    url(r'^system/changlog$', views.changlog, name='system_changelog'),
    url(r'^system/visitlog$', views.visitlog, name='system_visitlog'),
    url(r'^system/ajax_get_visitlog$', views.ajax_get_visitlog, name='ajax_get_visitlog'),
    url(r'^system/authlog$', views.authlog, name='system_authlog'),
    url(r'^system/ajax_get_authlog$', views.ajax_get_authlog, name='ajax_get_authlog'),
]

__all__ = ["urlpatterns"]