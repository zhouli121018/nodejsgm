# -*- coding: utf-8 -*-
#

from django.conf.urls import url

from app.mosaico import views

# app_name = 'mosaico'
urlpatterns = [
    url(r'^create/$', views.create, name="mosaico_create"),
    url(r'^mdf/(?P<template_id>\d+)/$', views.template_modify, name='mosaico_template_modify'),
    url(r'^start/(?P<template_id>\d+)/$', views.start, name='mosaico_start'),
    url(r'^get/(?P<template_id>\d+)/$', views.get, name='mosaico_get'),

    url(r'^$', views.index, name="mosaico_index"),
    url(r'^img/$', views.image, name="mosaico_img"),
    url(r'^upload/(?P<user_id>\d+)/$', views.upload, name="mosaico_upload"),
    url(r'^dl/$', views.download, name="mosaico_download"),
    url(r'^template/$', views.template, name="mosaico_template"),
]

