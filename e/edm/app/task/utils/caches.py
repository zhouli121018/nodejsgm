# -*- coding:utf-8 -*-

from django.core.cache import cache
from django.template import loader, Context
from app.task.models import SendTask

# key
# :django:proj:page:url:flag:user_id:task_id:

def cache_latest_task(request):
    lang = ( request.user.lang_code == 'en-us' and 'en-us') or "zh-hans"
    key = ":django:edmweb:home:home:task:{user_id}:{lang}:".format(user_id=request.user.id, lang=lang)
    content = cache.get(key, None)
    if not content:
        task_objs = SendTask.objects.filter(user_id=request.user.id, send_status=3).order_by('-id')[:7]
        t = loader.get_template('task/cache_latest_task.html')
        c = Context({ 'task_objs': task_objs})
        content = t.render(c)
        cache.set(key, content, 1800)
    return content
