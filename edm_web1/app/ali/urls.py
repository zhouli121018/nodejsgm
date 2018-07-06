from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^pre_pay$', views.pre_pay, name='ali_pre_pay'),
    url(r'^notify/$', views.alipay_notify_url, name='alipay_notify_url'),
    url(r'^return/$', views.alipay_return_url, name='alipay_return_url'),
    url(r'^login/$', views.ali_login, name='ali_login'),
    url(r'^login_return/$', views.ali_login_return, name='ali_login_return'),
]
