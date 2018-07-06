from django.conf.urls import url
from . import views
from django.conf.urls import include
from django_weixin.views import basic

urlpatterns = [
    url(r'^$', views.wechat, name='wechat'),
    #url(r'^$', basic.index, name='wechat'),
    url(r'^bind_wechat/$', views.bind_wechat, name='bind_wechat'),
    url(r'^bind_img$', views.bind_img, name='bind_img'),
    url(r'^ajax_check_bind/$', views.ajax_check_bind, name='ajax_check_bind'),
    url(r'^callback$', views.callback, name='wx_callback'),
    url(r'^payback$', views.payback, name='wx_payback'),

    url(r'^pre_pay/$', views.pre_pay, name='wx_pre_pay'),
    url(r'^pay_qrcode/(?P<product_id>\w+).png$', views.pay_qrcode, name='pay_qrcode'),
    url(r'^pay_success/$', views.pay_success, name='pay_success'),
    url(r'^pay_notify$', views.pay_notify, name='pay_notify'),
    url(r'^create_menu$', views.create_menu, name='wx_create_menu'),

    url(r'^access/', include('django_weixin.urls')),
]
