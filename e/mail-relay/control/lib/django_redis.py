# coding=utf-8
"""
根据django的配置　来获取不同服务器的redis
应用时　需导入django环境
"""

from redis_cache import get_redis_connection
from django.conf import settings


def get_redis():
    server_id = settings.SERVER_ID if settings.SERVER_ID else 'default'
    return get_redis_connection(server_id)
