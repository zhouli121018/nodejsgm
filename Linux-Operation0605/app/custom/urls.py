# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^custom_kkserver$', views.custom_kkserver_settings, name='custom_kkserver'),
]
