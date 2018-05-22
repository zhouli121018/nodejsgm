from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^mail_accurate/$', views.mail_accurate_service, name='mail_accurate_service'),
    url(r'^ajax_mail_accurate_open/$', views.ajax_mail_accurate_open, name='ajax_mail_accurate_open'),
]