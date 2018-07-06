# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import ckviews as views

urlpatterns = [
    # ckeditor
    url(r'^ck/(?P<template_id>\d+)/$', views.template_add, name='ck_template'),
    url(r'^ck/upload/(?P<template_id>\d+)/$', views.ckupload, name='ck_upload'),
    url(r'^ck/ref/$', views.ajax_ref_template, name='ck_reftemplate'),
]