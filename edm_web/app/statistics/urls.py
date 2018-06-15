# coding=utf-8
from django.conf.urls import url
from . import views, pdf_views

urlpatterns = [
    url(r'^$', views.mail_statistics, name='mail_statistics'),
    url(r'^ajax/$', views.ajax_mail_statistics, name='ajax_mail_statistics'),
    url(r'^export$', views.mail_statistics_export, name='mail_statistics_export'),
    url(r'^export/fail/$', views.export_fail_addr_statistics, name='export_fail_addr_statistics'),
    url(r'^batch$', views.batch_statistics, name='batch_statistics'),
    url(r'^batch/ajax$', views.ajax_batch_statistics, name='ajax_batch_statistics'),
    url(r'^sender$', views.sender_statistics, name='sender_statistics'),
    url(r'^sender/ajax$', views.ajax_sender_statistics, name='ajax_sender_statistics'),
    url(r'^clear/erraddr/$', views.ajax_clear_erraddr, name='ajax_clear_erraddr'),

    url(r'^report/(?P<task_id>\d+)/$', views.mail_statistics_report, name='mail_statistics_report'),
    url(r'^ajax_mail_statistics_report/(?P<task_id>\d+)/$', views.ajax_mail_statistics_report, name='ajax_mail_statistics_report'),

    url(r'^report/pdf/(?P<task_id>\d+)/$', pdf_views.mail_statistics_report_pdf, name='mail_statistics_report_pdf'),

    url(r'^world_mill_en/$', views.world_mill_en, name='world_mill_en'),
    url(r'^china_mill_zh/$', views.china_mill_zh, name='china_mill_zh'),
]

