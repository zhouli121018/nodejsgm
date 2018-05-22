# -*- coding:utf-8 -*-

from django.core.cache import cache
from app.core.models import CoreNotice, CoreNoticeLog, CoreNotification
from lib.parse_html2text import delhtml2text_2
from django.template import loader, Context, RequestContext

# :django:proj:page:url:flag:user_id:task_id:
# 公告
AJAX_CUSTOMER_MESSAGE_CACHE_KEY = ":django:edmweb:home:ajax_customer_message:message:{user_id}:{lang}:"
# 站内通知
CUSTOMER_NOTICE_CACHE_KEY = ":django:edmweb:home:ajax_core_notification:notice:{user_id}::"

# 公告
def customer_message(request):
    return ajax_customer_message(request)

def ajax_customer_message(request):
    # lang_code = ( request.user.lang_code == 'en-us' and 'en-us') or "zh-hans"
    lang_code = "1"
    key = AJAX_CUSTOMER_MESSAGE_CACHE_KEY.format(user_id=request.user.id, lang=lang_code)
    content = cache.get(key, None)
    if not content:
        lists = CoreNotice.objects.all().order_by('-id')
        read_lists, unread_lists = [], []
        for obj in lists:
            _existed = CoreNoticeLog.objects.filter(notice_id=obj.id, customer_id=request.user.id).exists()
            if _existed:
                content = delhtml2text_2(obj.content)
                if len(read_lists) >= 5:
                    continue
                read_lists.append((obj.id, obj.title, content, obj.start_time.strftime('%Y-%m-%d')))
            else:
                content = delhtml2text_2(obj.content)
                unread_lists.append((obj.id, obj.title, content, obj.start_time.strftime('%Y-%m-%d')))
        t = loader.get_template('setting/ajax_customer_message.html')
        c = Context({ 'read_lists': read_lists, 'unread_lists': unread_lists })
        # c = RequestContext(request, { 'read_lists': read_lists, 'unread_lists': unread_lists } )
        content = t.render(c)
        cache.set(key, content, 1800)
    return content

# 通知
def ajax_core_notification(request):
    key = CUSTOMER_NOTICE_CACHE_KEY.format(user_id=request.user.id)
    content = cache.get(key, None)
    if not content:
        lists1 = CoreNotification.objects.filter(customer_id=request.user.id, is_read=True).order_by('-id')[:5]
        lists2 = CoreNotification.objects.filter(customer_id=request.user.id, is_read=False).order_by('-id')[:15]
        read_lists, unread_lists = [], []
        for obj in lists1:
            content = delhtml2text_2(obj.content)
            read_lists.append((obj.id, obj.subject, content, obj.created.strftime('%Y-%m-%d %H:%M')))
        for obj in lists2:
            content = delhtml2text_2(obj.content)
            unread_lists.append((obj.id, obj.subject, content, obj.created.strftime('%Y-%m-%d %H:%M')))
        t = loader.get_template('setting/ajax_core_notification.html')
        c = Context({ 'read_lists': read_lists, 'unread_lists': unread_lists })
        content = t.render(c)
        cache.set(key, content, 1800)
    return content