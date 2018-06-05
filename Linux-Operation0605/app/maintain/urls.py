# -*- coding: utf-8 -*-

from django.conf.urls import url
from app.maintain import views

urlpatterns = [
    # url(r'^ssl/$', views.sslView, name='ssl_maintain'),
    # url(r'^ssl/enable$', views.sslEnableView, name='sslEnableView'),
    # url(r'^ssl/private$', views.sslPrivateView, name='sslPrivateView'),
    # url(r'^ssl/sign$', views.sslSignatureView, name='sslSignatureView'),
    # url(r'^ssl/cert$', views.sslCertView, name='sslCertView'),
    url(r'^backup/$', views.backupView, name='backup_maintain'),
    url(r'^backup/set/$', views.backupSetView, name='backupset_maintain'),
    url(r'^log/$', views.logView, name='log_maintain'),
    url(r'^isolate/$', views.isolateView, name='isolate_maintain'),
    url(r'^isolate/ajax$', views.isolateAjaxView, name='isolate_ajax_maintain'),
]
