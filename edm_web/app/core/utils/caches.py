# -*- coding:utf-8 -*-

from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from tagging.models import TagCategory, Tag, TaggedItem
from app.core.models import Prefs

# :django:proj:page:url:flag:user_id:task_id:
# 开启精准服务客户
OPEN_ACCURATE_KEY = ":django:edmweb:accurate:all:all:{user_id}::"
# 父标签
TAG_PARENT_CACHE_KEY = ":django:edmweb:address:mail_accurate_service:parenttag:{tag_type}:{is_show}:"
# 子标签
TAG_CHILD_CACHE_KEY = ":django:edmweb:address:mail_accurate_service:childtag:{parent_id}::"

# 保存搜索标签
def cache_search_address_tags():
    seach_tags = cache.get("edm_web:tagging:tag:address")
    if not seach_tags:
        seach_tags = Tag.objects.filter(category__category='address')
        cache.set("edm_web:tagging:tag:address", seach_tags, 3600)
    return seach_tags

# 开启精准数据服务
def cache_open_accurate(request):
    status = False
    service_obj = request.user.service()
    if service_obj.is_open_accurate:
        status = True
    else:
        m_service, _ = Prefs.objects.get_or_create(name='min_accurate_service_qty')
        min_accurate_service_qty = int(m_service.value) if m_service.value else None
        if not status and min_accurate_service_qty and service_obj.qty_buytotal >= min_accurate_service_qty:
            status = True
            service_obj.is_open_accurate = True
            service_obj.save()
    return status

    key = OPEN_ACCURATE_KEY.format(user_id=request.user.id)
    status = cache.get(key, None)
    if status is None:
        status = False
        service_obj = request.user.service()
        if service_obj.is_open_accurate:
            status = True
        else:
            m_service, _ = Prefs.objects.get_or_create(name='min_accurate_service_qty')
            min_accurate_service_qty = int(m_service.value) if m_service.value else None
            if not status and min_accurate_service_qty and service_obj.qty_buytotal>=min_accurate_service_qty:
                status = True
                service_obj.is_open_accurate = True
                service_obj.save()
        cache.set(key, status, 3600)
    return status

def cache_parent_tags(tag_type="address", is_show=True):
    key = TAG_PARENT_CACHE_KEY.format(tag_type=tag_type, is_show=is_show)
    tag_lists = cache.get(key, None)
    if not tag_lists:
        tag_lists = []
        cat_lists = TagCategory.objects.filter(category=tag_type)
        if is_show:
            cat_lists = cat_lists.filter(is_show=True)
        cat_lists = cat_lists.order_by('order_id', 'id')
        for d in cat_lists:
            lists = Tag.objects.filter(category=d.id, parent__isnull=True).order_by('order_id', 'id')
            tag_lists.append([d.id, d.name, lists])
        cache.set(key, tag_lists, 3600)
    return tag_lists

def cache_child_tags(parent_id):
    key = TAG_CHILD_CACHE_KEY.format(parent_id=parent_id)
    tag_lists = cache.get(key, None)
    if not tag_lists:
        tag_lists = Tag.objects.filter(parent_id=parent_id).order_by('order_id', 'id')
        cache.set(key, tag_lists, 3600)
    return tag_lists