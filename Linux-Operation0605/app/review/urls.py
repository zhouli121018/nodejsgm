# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^$', views.review_list, name='review_list'),
    # url(r'^add/$', views.review_add, name='review_add'),
    # url(r'^mdf/(?P<review_id>\d+)/$', views.review_modify, name='review_modify'),
    # url(r'^choose/$', views.choose_review_list, name='choose_review_list'),
    #
    # url(r'^rule/$', views.reviewrule_list, name='reviewrule_list'),
    # url(r'^rule/ajax/$', views.ajax_reviewrule_list, name='ajax_reviewrule_list'),
    # url(r'^rule/add/$', views.reviewrule_add, name='reviewrule_add'),
    # url(r'^rule/(?P<rule_id>\d+)/$', views.reviewrule_modify, name='reviewrule_modify'),
    #
    # url(r'^config/$', views.review_config, name='review_config'),
]
