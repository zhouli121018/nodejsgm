# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.domainHome, name='domain_home'),
    url(r'^basic$', views.domainBasic, name='domain_basic'),
    url(r'^reg_login/$', views.domainRegLogin, name='domain_reg_login'),
    url(r'^sys/$', views.domainSys, name='domain_sys'),
    url(r'^sys/pwd_extra$', views.domainSysPasswordExtra, name='domain_sys_pwd_extra'),
    url(r'^webmail/$', views.domainWebmail, name='domain_webmail'),
    url(r'^sign/$', views.domainSign, name='domain_sign'),
    url(r'^module/$', views.domainModule, name='domain_module'),
    url(r'^public/$', views.domainPublicList, name='domain_public'),
    url(r'^secret/$', views.domainSecret, name='domain_secret'),
]
