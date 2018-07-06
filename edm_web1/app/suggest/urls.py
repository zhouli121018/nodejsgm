from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^ajax/$', views.ajax_suggest, name='ajax_suggest'),
    url(r'^ajax/post/$', views.ajax_suggest_post, name='ajax_suggest_post'),
]