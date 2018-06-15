# coding=utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.task_list, name='task_list'),
    url(r'^add/$', views.task_add, name='task_add'),
    url(r'^ajax_load_template/$', views.ajax_load_template, name='ajax_load_template'),
    url(r'^modify/(?P<task_id>\d+)/$', views.task_modify, name='task_modify'),
    url(r'^view/(?P<task_id>\d+)/$', views.task_view, name='task_view'),
    url(r'^ajax_task_list/$', views.ajax_task_list, name='ajax_task_list'),
    url(r'^ajax_pause_task/(?P<task_id>\d+)/$', views.ajax_pause_task, name='ajax_pause_task'),

    url(r'^ajax_stat_info/(?P<task_id>\d+)/$', views.ajax_stat_info, name='ajax_stat_info'),
    url(r'^ajax_template_info/(?P<task_id>\d+)/$', views.ajax_template_info, name='ajax_template_info'),
    url(r'^ajax_stat_success_info/(?P<task_id>\d+)/$', views.ajax_stat_success_info, name='ajax_stat_success_info'),

    # 通过分类 获取获取联系人地址数量
    url(r'^ajax_get_maillist_count/$', views.ajax_get_maillist_count, name='ajax_get_maillist_count'),
    # 通过分类 获取获取联系人地址数量 以及 触发器
    url(r'^ajax_get_maillist_trigger/$', views.ajax_get_maillist_trigger, name='ajax_get_maillist_trigger'),
    # 通过分类 获取获取联系人地址数量 以及 触发器
    url(r'^ajax_get_maillistcount_and_triggers/$', views.ajax_get_maillistcount_and_triggers, name='ajax_get_maillistcount_and_triggers'),
    # 通过域名 获取发件人邮箱
    url(r'^ajax_get_mailbox/$', views.ajax_get_mailbox, name='ajax_get_mailbox'),

    # 检测跟踪域名
    url(r'^ajax_check_track_domain/$', views.ajax_check_track_domain, name='ajax_check_track_domain'),

    # 邮件内容模板阅读
    url(r'^preview/(?P<content_id>\d+)/$', views.task_preview, name='task_preview'),

    # 最近任务缓存
    url(r'^ajax_cache_latest_task/$', views.ajax_cache_latest_task, name='ajax_cache_latest_task'),
]
