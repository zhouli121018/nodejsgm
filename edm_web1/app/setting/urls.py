from django.conf.urls import url
from . import views, user_views, share_views

urlpatterns = [
    url(r'^account/$', views.customer_account, name='account'),
    url(r'^ajax_alter_customer_field/$', views.ajax_alter_customer_field, name='ajax_alter_customer_field'),

    url(r'^other/set/$', views.other_settings, name='other_settings'),

    url(r'^security/$', views.customer_security, name='security'),
    url(r'^security/password/modify/$', views.core_password_modify, name='core_password_modify'),
    url(r'^security/login_safe/$', views.core_login_safe_set, name='core_login_safe_set'),
    url(r'^ajax_check_paasswd/$', views.ajax_check_paasswd, name='ajax_check_paasswd'),
    url(r'^ajax_check_login_ip/$', views.ajax_check_login_ip, name='ajax_check_login_ip'),
    url(r'^security/token/$', views.customer_token, name='customer_token'),
    url(r'^ajax_customer_token/$', views.ajax_customer_token, name='ajax_customer_token'),
    url(r'^ajax_create_token/$', views.ajax_create_token, name='ajax_create_token'),

    url(r'^notice/$', views.customer_notice, name='notice'),
    url(r'^notice/create/$', views.customer_notice_create, name='customer_notice_create'),
    url(r'^notice/modify/(?P<notice_id>\d+)/$', views.customer_notice_modify, name='customer_notice_modify'),
    url(r'^ajax_customer_notice/$', views.ajax_customer_notice, name='ajax_customer_notice'),
    url(r'^ajax_check_notice_param/$', views.ajax_check_notice_param, name='ajax_check_notice_param'),
    url(r'^ajax_notice_detail/$', views.ajax_notice_detail, name='ajax_notice_detail'),

    url(r'^order/$', views.customer_order, name='order'),
    url(r'^order/ajax/$', views.ajax_order, name='ajax_order'),
    url(r'^order/ajax/notapply/$', views.ajax_check_order_notapply, name='ajax_check_order_notapply'),

    url(r'^invoiceinfo/$', views.customer_invoice_baseinfo, name='customer_invoice_baseinfo'),
    url(r'^invoice/upload/$', views.customer_invoice_upload, name='customer_invoice_upload'),
    url(r'^invoice/upload/view/$', views.customer_invoice_upload_view, name='customer_invoice_upload_view'),
    url(r'^invoice/$', views.customer_invoice, name='invoice'),
    url(r'^invoice/ajax/$', views.ajax_invoice, name='ajax_invoice'),
    url(r'^invoice/create/$', views.customer_invoice_create, name='customer_invoice_create'),
    url(r'^invoice/view/(?P<invoice_id>\d+)/$', views.customer_invoice_view, name='customer_invoice_view'),

    url(r'^operate/log/$', views.customer_operate_log, name='operate_log'),
    url(r'^ajax_operate_log/$', views.ajax_operate_log, name='ajax_operate_log'),
    url(r'^operate/log/return/$', views.customer_operate_log_return, name='operate_log_return'),

    url(r'^invalid/addr/$', views.customer_invalid_address, name='invalid_address'),
    url(r'^invalid/addr/delete/$', views.ajax_delete_invalid_address, name='ajax_delete_invalid_address'),


    url(r'^customer_bind/$', views.customer_bind, name='customer_bind'),
    url(r'^wx_check_info/$', views.wx_check_info, name='wx_check_info'),
    url(r'^customer_bind_success/$', views.customer_bind_success, name='customer_bind_success'),
    url(r'^customer_unbind_success/$', views.customer_unbind_success, name='customer_unbind_success'),

    url(r'^ajax_add_order/$', views.ajax_add_order, name='ajax_add_order'),
    url(r'^ajax_check_order/$', views.ajax_check_order, name='ajax_check_order'),

    url(r'^pricing/$', views.pricing, name='pricing'),
    url(r'^pre_pricing/(?P<id>\d+)/$', views.modal_pre_pricing, name='modal_pre_pricing'),

    url(r'^complaint/$', views.customer_complaint, name='customer_complaint'),
    url(r'^ajax_complaint/$', views.ajax_complaint, name='ajax_complaint'),

    url(r'^message/$', views.customer_message, name='customer_message'),
    url(r'^ajax_customer_message/$', views.ajax_customer_message, name='ajax_customer_message'),
    url(r'^message/ajax/$', views.ajax_customer_notice_active, name='ajax_customer_notice_active'),
    url(r'^message/log/(?P<notice_id>\d+)/$', views.customer_message_log, name='customer_message_log'),

    url(r'^notify/$', views.core_notification, name='core_notification'),
    url(r'^ajax_core_notification/$', views.ajax_core_notification, name='ajax_core_notification'),
    url(r'^notify/(?P<notify_id>\d+)/$', views.core_notification_log, name='core_notification_log'),

    url(r'^notify/lists/$', views.core_notification_lists, name='core_notification_lists'),
    url(r'^notify/lists/ajax/$', views.ajax_core_notification_lists, name='ajax_core_notification_lists'),


    url(r'^sub_account/$', user_views.sub_account, name='sub_account'),
    url(r'^sub_account/create/$', user_views.sub_account_create, name='sub_account_create'),
    url(r'^sub_account/set/(?P<user_id>\d+)/$', user_views.sub_account_setcus, name='sub_account_setcus'),
    url(r'^sub_account/reset/(?P<user_id>\d+)/$', user_views.sub_account_reset, name='sub_account_reset'),
    # url(r'^sub_account/perm/(?P<user_id>\d+)/$', user_views.sub_account_perm, name='sub_account_perm'),
    url(r'^sub_account/modify/(?P<user_id>\d+)/$', user_views.sub_account_modify, name='sub_account_modify'),
    url(r'^sub_account/reback/(?P<user_id>\d+)/$', user_views.sub_account_reback, name='sub_account_reback'),
    url(r'^sub_account/share/(?P<user_id>\d+)/$', user_views.sub_account_share, name='sub_account_share'),
    url(r'^sub_account/ajax/share/$', user_views.sub_account_share_ajax, name='sub_account_share_ajax'),
     url(r'^sub_account/ajax/share/del$', user_views.sub_account_share_del_ajax, name='sub_account_share_del_ajax'),
    url(r'^eh5a5NN0kTY71daFlBm1A1$', user_views.sub_account_login, name='sub_account_login'),

    url(r'^rcpblack/$', views.rcpblack, name='rcpblack'),
    url(r'^rcpblack/ajax/$', views.ajax_rcpblack, name='ajax_rcpblack'),
    url(r'^rcpblack/add/$', views.rcpblack_add, name='rcpblack_add'),
    url(r'^rcpblack/batchadd/$', views.rcpblack_batchadd, name='rcpblack_batchadd'),
    url(r'^rcpblack/(?P<black_id>\d+)/$', views.rcpblack_modify, name='rcpblack_modify'),

    url(r'^addrshare/(?P<user_id>\d+)/$', share_views.sub_share_addr, name='sub_share_addr'),
    url(r'^addrshare/ajax/(?P<user_id>\d+)/$', share_views.sub_share_addr_ajax, name='sub_share_addr_ajax'),

    url(r'^tplshare/(?P<user_id>\d+)/$', share_views.sub_share_template, name='sub_share_template'),
    url(r'^tplshare/ajax/(?P<user_id>\d+)/$', share_views.sub_share_template_ajax, name='sub_share_template_ajax'),
]