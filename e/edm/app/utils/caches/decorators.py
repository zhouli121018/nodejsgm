# -*- coding: utf-8 -*-
import json
import hashlib
from functools import wraps
from django.conf import settings
from django.core.cache import caches
from django.utils.decorators import available_attrs
from .tools import get_unique_method_id, get_unique_method_id2

def get_cache(alias):
    return caches[alias]

class CacheResponse(object):

    def __init__(self, timeout=1800, key_prefix=None, cache="limitip", posturl=None, single_user=True):
        """
        :param timeout:      超时时间
        :param key_prefix:   key 前缀
        :param cache:        缓存数据库
        :param posturl:      提交时的url,作用于清除缓存
        :param single_user:  True单个用户， single_user 所有用户，
        :return:
        """
        self.timeout=timeout
        self.key_prefix=key_prefix or "edmweb"
        self._cache = cache
        self.cache = get_cache(cache or settings.USER_AGENTS_CACHE)
        self.posturl = posturl
        self.single_user = single_user

    def __call__(self, func):
        @wraps(func, assigned=available_attrs(func))
        def inner(request, *args, **kwargs):
            return self.process_cache_response(
                view_method=func,
                request=request,
                args=args,
                kwargs=kwargs,
            )
        return inner

    def process_cache_response(self, view_method, request, args, kwargs):
        if request.method.lower() == "post":
            set_delete_cache_withpost(request, cache=self._cache, key_prefix=self.key_prefix, url=self.posturl or request.path)
            return view_method(request, *args, **kwargs)
        elif request.method.lower() == "get":
            deletekey = get_delete_key(request, key_prefix=self.key_prefix, url=self.posturl or request.path)
            getkwargs = dict(request.GET)
            key = self.get_key(
                view_method=view_method,
                request=request,
                args=args,
                kwargs=kwargs,
                getkwargs=getkwargs,
            )
            if self.cache.has_key(deletekey):
                self.cache.delete(deletekey)
                self.cache.delete(key)
                response = view_method(request, *args, **kwargs)
            else:
                response = self.cache.get(key)
                if not response:
                    response = view_method(request, *args, **kwargs)
                    if not response.status_code >= 400:
                        self.cache.set(key, response, self.timeout)
            return response

    def get_key(self, view_method, request, args, kwargs, getkwargs):
        keydict = json.dumps({
            'unique_method_id': get_unique_method_id(view_method, request),
            'args': args,
            'kwargs': kwargs,
            'getkwargs': getkwargs,
            'instance_id': id(self)
        })
        key = hashlib.md5(json.dumps(keydict, sort_keys=True).encode('utf-8')).hexdigest()
        if request.user.is_authenticated and self.single_user:
            return "{}:{}:{}".format(self.key_prefix, request.user.id, key)
        return "{}:{}".format(self.key_prefix, key)

def get_delete_key(request, key_prefix='edmweb', url=None):
    url = url or request.path
    key = get_unique_method_id2('get_delete_key', url)
    if request.user.is_authenticated:
        return "{}:{}:{}".format(key_prefix, request.user.id, key)
    return "{}:{}".format(key_prefix, key)

def set_delete_cache_withpost(request, cache='limitip', url=None, key_prefix='edmweb', timout=1800):
    key = get_delete_key(request, url=url, key_prefix=key_prefix)
    cache = get_cache(cache or settings.USER_AGENTS_CACHE)
    cache.set(key, '1', timout)

cache_response = CacheResponse