from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import login, logout
from wiki.urls import get_pattern as get_wiki_pattern
from django_nyt.urls import get_pattern as get_nyt_pattern
from ajax_select import urls as ajax_select_urls

urlpatterns = [
                  # Examples:
                  url(r'^notifications/', get_nyt_pattern()),
                  url(r'^help/', get_wiki_pattern()),
                  url(r'^rest/', include('apps.rest.urls')),
                  url(r'^$', 'web.views.home', name='home'),
                  url(r'^core/', include('apps.core.urls')),
                  url(r'^mail/', include('apps.mail.urls')),
                  url(r'^tools/', include('apps.mail.tools_urls')),
                  url(r'^mail_review/', include('apps.mail.review_urls')),
                  url(r'^setting/', include('apps.mail.setting_urls')),
                  url(r'^check_list/', include('apps.mail.check_list_urls')),
                  url(r'^tech_support/', include('apps.mail.tech_support_urls')),
                  url(r'^flag/', include('apps.flag.urls')),
                  url(r'^collect/', include('apps.collect.urls')),
                  url(r'^collect_mail/', include('apps.collect_mail.urls')),
                  url(r'^cmail/', include('apps.collect_mail.urls')),
                  url(r'^collect_mail_review/', include('apps.collect_mail.review_urls')),
                  url(r'^cmail_review/', include('apps.collect_mail.review_urls')),
                  # url(r'^collect_check_list/', include('apps.collect_mail.check_list_urls')),
                  # url(r'^collect_setting/', include('apps.collect_mail.setting_urls')),
                  url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                  url(r'^admins/', include('apps.core.admins_urls')),

                  url(r'^api_search/', include('apps.mail.api_urls')),

                  url(r'^ajax_select/', include(ajax_select_urls)),

                  url(r'^admin/', include(admin.site.urls)),
                  url(r'^login$', login,  {'template_name': 'login.html'}, name='my_login'),
                  url(r'^logout$', logout, {'template_name': 'logout.html'}, name='logout'),
                  url(r'^ajax_get_remark_base$', 'web.views.ajax_get_remark_base', name='ajax_get_remark_base'),
                  url(r'^ajax_save_remark_base$', 'web.views.ajax_save_remark_base', name='ajax_save_remark_base'),

                  url(r'^localized_mail/', include('apps.localized_mail.urls')),
              ] + staticfiles_urlpatterns()

