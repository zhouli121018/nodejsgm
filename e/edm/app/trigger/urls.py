from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^set$', views.trigger, name='trigger'),
    url(r'^add/$', views.trigger_add, name='trigger_add'),
    url(r'^modify/(?P<trig_id>\d+)/$', views.trigger_modify, name='trigger_modify'),
    url(r'^show/(?P<trig_id>\d+)/$', views.trigger_show, name='trigger_show'),
    url(r'^action/add/(?P<trig_id>\d+)/$', views.trigger_action_add, name='trigger_action_add'),
    url(r'^action/modify/(?P<trig_id>\d+)/(?P<action_id>\d+)/$', views.trigger_action_modify, name='trigger_action_modify'),
    url(r'^$', views.trigger_task, name='trigger_task'),
    url(r'^ajax_task$', views.ajax_trigger_task, name='ajax_trigger_task'),

    url(r'^task/(?P<task_id>\d+)/$', views.trigger_task_one, name='trigger_task_one'),
    url(r'^ajax_task_one/(?P<task_id>\d+)/$', views.ajax_trigger_task_one, name='ajax_trigger_task_one'),
    url(r'^template_preview/(?P<template_id>\d+)/$', views.template_preview, name='trigger_template_preview'),
]

