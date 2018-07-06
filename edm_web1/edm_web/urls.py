# -*- coding: utf-8 -*-

"""edm_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include

from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from edm_web import views, forms, register
# from edm_web import views, forms
from django.conf import settings
from app.track.views import track_statistic, track_statistic2, track_statistic3, track_statistic4
from app.template.ckviews import share, ajax_view_template

urlpatterns = [
                  url(r'^captcha/', include('captcha.urls')),

                  url(r'^core/', include('app.core.urls')),
                  url(r'^trigger/', include('app.trigger.urls')),
                  url(r'^service/', include('app.core.service_urls')),
                  url(r'^address/', include('app.address.urls')),
                  url(r'^template/', include('app.template.urls')),
                  url(r'^task/', include('app.task.urls')),
                  url(r'^track/', include('app.track.urls')),
                  url(r'^setting/', include('app.setting.urls')),
                  url(r'^statistics/', include('app.statistics.urls')),
                  url(r'^wechat/', include('app.wechat.urls')),
                  url(r'^ali/', include('app.ali.urls')),
                  url(r'^mosaico/', include('app.mosaico.urls')),
                  url(r'^suggest/', include('app.suggest.urls')),

                  url(r'^login$', login, {'template_name': 'login.html', 'authentication_form': forms.CustomizeAuthenticationForm}, name='my_login'),
                  url(r'^logout$', logout, {'template_name': 'logout.html'}, name='logout'),
                  url(r'^passwd/reset$', views.password_reset, {'template_name': 'password_reset.html'}, name='password_reset'),
                  url(r'^ajax_check_username$', views.ajax_check_username, name='ajax_check_username'),
                  url(r'^passwd/done$', views.password_reset_done, {'template_name': 'password_reset_done.html'}, name='password_reset_done'),
                  url(r'^passwd/set$', views.password_set, {'template_name': 'password_set_form.html'}, name='password_set'),
                  url(r'^ZmE2MmIxYzMwM2Fm$', views.php_login, name='php_login'),
                  url(r'^admin/', admin.site.urls),

                  url(r'^ajax_checkusername_and_smscode$', views.ajax_checkusername_and_smscode, name='ajax_checkusername_and_smscode'),
                  url(r'^ajax_checkusername_and_checksmscode$', views.ajax_checkusername_and_checksmscode, name='ajax_checkusername_and_checksmscode'),

                  # url(r'^register_new_step3/$', register.register_new_step3, name='register_new_step3'),
                  # url(r'^register_new_step2/$', register.register_new_step2, name='register_new_step2'),
                  # url(r'^register_new/$', register.register_new, name='register_new'),
                  url(r'^register_login/$', register.register_login, name='register_login'),

                  url(r'^register_new/$', register.apply, name='apply'),
                  url(r'^register_step2/$', register.apply_step2, name='apply_step2'),

                  url(r'^register/$', views.register, name='register'),
                  url(r'^ajax_smscode$', register.ajax_smscode, name='ajax_smscode'),
                  url(r'^ajax_checksmscode$', register.ajax_checksmscode, name='ajax_checksmscode'),

                  url(r'^$', views.home, name='home'),
                  url(r'^lang/set/$', views.set_lang, name='set_lang'),
                  url(r'^MP_verify_qtROZ0sDp2gDeaQI.txt$', views.js_oauth_verify),
                  url(r'^new_track/t/(?P<track_params>.*?)$', track_statistic, name='track_statistic'),
                  url(r'^new_track/t2/(?P<track_params>.*?)$', track_statistic2, name='track_statistic2'),
                  url(r'^new_track/t3/(?P<track_params>.*?)$', track_statistic3, name='track_statistic3'),
                  url(r'^new_track/t4/(?P<track_params>.*?)$', track_statistic4, name='track_statistic4'),

                  url(r'^ajax_save_remark_base$', views.ajax_save_remark_base, name='ajax_save_remark_base'),
                  url(r'^ajax_get_remark_base$', views.ajax_get_remark_base, name='ajax_get_remark_base'),

                  # 共享链接
                  url(r'^share/$', share, name='ck_share'),
                  # 无法查看
                  url(r'^p/$', ajax_view_template, name='ajax_view_template'),
                  url(r'^ajax_get_captcha$', views.ajax_get_captcha, name='ajax_get_captcha'),
                  url(r'^captcha_img/(?P<file_id>.*?)$', views.captch_img, name='captcha_img'),
                  url(r'^ajax_check_captcha/$', views.ajax_check_captcha, name='ajax_check_captcha'),
              ] + staticfiles_urlpatterns()

from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

