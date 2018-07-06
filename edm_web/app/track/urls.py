# coding=utf-8
from django.conf.urls import url
from . import views
from app.statistics import pdf_views

urlpatterns = [
    url(r'^t/(?P<track_params>.*?)$', views.track_statistic, name='old_track_statistic'),
    url(r'^t2/(?P<track_params>.*?)$', views.track_statistic2, name='old_track_statistic2'),

    # 邮件跟踪
    # 邮件跟踪 smtp发送 兼容设置
    url(r'^trackstat/$', views.track_task_stat, name='track_task_stat'),
    url(r'^ajax_track_task_link/$', views.ajax_track_task_link, name='ajax_track_task_link'),
    url(r'^task/pdf/$', pdf_views.track_task_pdf, name='track_task_pdf'),

    url(r'^open/$', views.track_open_info, name='track_open_info'),
    url(r'^click/$', views.track_click_info, name='track_click_info'),

    url(r'^email/(?P<track_id>\d+)/$', views.track_email, name='track_email'),
    url(r'^click/(?P<track_id>\d+)/$', views.track_click, name='track_click'),

    url(r'^ajax_track_email/$', views.ajax_track_email, name='ajax_track_email'),
    url(r'^ajax_track_click/$', views.ajax_track_click, name='ajax_track_click'),
    url(r'^track_export_email/$', views.track_export_email, name='track_export_email'),
    url(r'^track_export_email_click/$', views.track_export_email_click, name='track_export_email_click'),
]

