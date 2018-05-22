# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views
from .ckurls import urlpatterns as ckurlpatterns

urlpatterns = [
    url(r'^$', views.template_list, name='template_list'),
    url(r'^modify/(?P<template_id>\d+)/$', views.template_modify, name='template_modify'),
    url(r'^preview/(?P<template_id>\d+)/$', views.template_preview, name='template_preview'),
    url(r'^test/history/(?P<template_id>\d+)/$', views.test_template_history, name='test_template_history'),
    url(r'^ajax_check_result_report/$', views.ajax_check_result_report, name='ajax_check_result_report'),
    url(r'^show_template_report/$', views.show_template_report, name='show_template_report'),
    # 定时 保存tmeplate
    url(r'^ajax_save_template/(?P<template_id>\d+)/$', views.ajax_save_template, name='ajax_save_template'),

    url(r'^ajax_multi_upload/(?P<template_id>\d+)/$', views.ajax_multi_upload, name='ajax_multi_upload'),

    url(r'^ajax_template_list/$', views.ajax_template_list, name='ajax_template_list'),
    url(r'^ajax_send_template$', views.ajax_send_template, name='ajax_send_template'),

    url(r'^ajax_template_id$', views.ajax_template_id, name='ajax_template_id'),
    url(r'^ajax_copy_template_id$', views.ajax_copy_template_id, name='ajax_copy_template_id'),
    url(r'^ajax_check_template_size/$', views.ajax_check_template_size, name='ajax_check_template_size'),
    url(r'^ajax_onchange_image_encode/$', views.ajax_onchange_image_encode, name='ajax_onchange_image_encode'),

    url(r'^ajax_get_content_from_url/(?P<template_id>\d+)/$', views.ajax_get_content_from_url, name='ajax_get_content_from_url'),
    url(r'^ajax_get_html_content/$', views.ajax_get_html_content, name='ajax_get_html_content'),

    url(r'^ajax_attachfile_upload/(?P<template_id>\d+)/$', views.ajax_attachfile_upload, name='ajax_attachfile_upload'),
    url(r'^ajax_delete_attach_id/$', views.ajax_delete_attach_id, name='ajax_delete_attach_id'),
    url(r'^ajax_download_attachfile/(?P<template_id>\d+)/(?P<attach_id>\d+)/$', views.ajax_download_attachfile, name='ajax_download_attachfile'),
    url(r'^ajax_get_network_attach/$', views.ajax_get_network_attach, name='ajax_get_network_attach'),
    url(r'^ajax_get_netatt/$', views.ajax_get_netatt, name='ajax_get_netatt'),

    url(r'^ajax_del_html_to_text/$', views.ajax_del_html_to_text, name='ajax_del_html_to_text'),

    url(r'^ajax_check_template_lang/$', views.ajax_check_template_lang, name='ajax_check_template_lang'),

    url(r'^ajax_unsubscribe_or_complaints/$', views.ajax_unsubscribe_or_complaints, name='ajax_unsubscribe_or_complaints'),
    url(r'^ajax_recipient_view_template/$', views.ajax_recipient_view_template, name='ajax_recipient_view_template'),

    url(r'^ajax_upload_json/$', views.ajax_upload_json, name='ajax_upload_json'),

    url(r'^ajax_get_ref_template_imglist/$', views.ajax_get_ref_template_imglist, name='ajax_get_ref_template_imglist'),
    url(r'^ajax_reftemplate_cover_htmlcontent/$', views.ajax_reftemplate_cover_htmlcontent, name='ajax_reftemplate_cover_htmlcontent'),
]

urlpatterns += ckurlpatterns

