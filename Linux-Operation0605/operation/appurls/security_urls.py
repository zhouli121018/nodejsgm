# -*- coding: utf-8 -*-
"""
安全设置
"""

from django.conf.urls import url
from app.fail2ban import views as fail2ban_views
from app.setting import views as setting_views

urlpatterns = [
    # i.	动态屏蔽
    url(r'^security/fail2ban/rulelist/$', fail2ban_views.fail2ban_rulelist, name='fail2ban_home'),
    url(r'^security/fail2ban/blocklist$', fail2ban_views.fail2ban_blocklist, name='fail2ban_blocklist'),
    url(r'^security/fail2ban/whitelist$', fail2ban_views.fail2ban_whitelist, name='fail2ban_whitelist'),

    url(r'^security/fail2ban/rulelist/ajax$', fail2ban_views.ajax_fail2ban_rulelist, name='ajax_fail2ban_rulelist'),
    url(r'^security/fail2ban/blocklist/ajax$', fail2ban_views.ajax_fail2ban_blocklist, name='ajax_fail2ban_blocklist'),
    url(r'^security/fail2ban/whitelist/ajax$', fail2ban_views.ajax_fail2ban_whitelist, name='ajax_fail2ban_whitelist'),

    url(r'^security/fail2ban/rulelist/new$', fail2ban_views.fail2ban_rulenew, name='fail2ban_rulenew'),
    url(r'^security/fail2ban/blocklist/new$', fail2ban_views.fail2ban_blocknew, name='fail2ban_blocknew'),
    url(r'^security/fail2ban/whitelist/new$', fail2ban_views.fail2ban_whitenew, name='fail2ban_whitenew'),

    url(r'^security/fail2ban/rulelist/mdf(?P<mdf_id>\d+)$', fail2ban_views.fail2ban_rulemdf, name='fail2ban_rulemdf'),
    url(r'^security/fail2ban/blocklist/mdf(?P<mdf_id>\d+)$', fail2ban_views.fail2ban_blockmdf, name='fail2ban_blockmdf'),
    url(r'^security/fail2ban/whitelist/mdf(?P<mdf_id>\d+)$', fail2ban_views.fail2ban_whitemdf, name='fail2ban_whitemdf'),

    # ii.	信任IP地址
    url(r'^security/set/trustip/$', setting_views.trustip_set, name='trustip_set'),
    url(r'^security/set/trustip/ajax$', setting_views.ajax_trustip_set, name='ajax_trustip_set'),


    # iii.	发件人黑/白名单
    url(r'^security/set/black/$', setting_views.blacklist, name='blacklist_set'),
    url(r'^security/set/black/ajax$', setting_views.ajax_blacklist, name='ajax_blacklist_set'),
    url(r'^security/set/white/$', setting_views.whitelist, name='whitelist_set'),
    url(r'^security/set/white/ajax$', setting_views.ajax_whitelist, name='ajax_whitelist_set'),

    # iv.	收件人白名单
    url(r'^security/set/white_rcp/$', setting_views.whitelist_rcp, name='whitelist_rcp_set'),
    url(r'^security/set/white_rcp/ajax$', setting_views.ajax_whitelist_rcp, name='ajax_whitelist_rcp_set'),


]

__all__ = ["urlpatterns"]
