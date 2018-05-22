from django.conf.urls import include, url

from django.contrib import admin
from django.contrib.auth.views import login, logout
from apps.core.forms import MyAuthenticationForm

urlpatterns = [
    # Examples:
    url(r'^$', 'web_customer.views.home', name='home'),
    url(r'^ajax_get_statistic$', 'web_customer.views.ajax_get_statistic', name='ajax_get_statistic'),
    url(r'^mail/', include('apps.mail.urls')),
    url(r'^core/', include('apps.core.urls')),
    url(r'^collect_mail/', include('apps.collect_mail.urls')),
    url(r'^login$', login,  {'template_name': 'login.html', 'authentication_form': MyAuthenticationForm}, name='my_login'),
    url(r'^logout$', logout, {'template_name': 'logout.html'}, name='logout'),
    url(r'^captcha/', include('captcha.urls')),

    # url(r'^admin/', include(admin.site.urls)),
    url(r'^lang/set/$', 'web_customer.views.set_lang', name='set_lang'),
    url(r'^ajax_get_remark_base$', 'web_customer.views.ajax_get_remark_base', name='ajax_get_remark_base'),
    url(r'^ajax_save_remark_base$', 'web_customer.views.ajax_save_remark_base', name='ajax_save_remark_base'),
]
