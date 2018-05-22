#coding=utf-8
import os
import random
import hashlib
import datetime

from django.conf import settings
# 随机字符生成种子
SEEDS  = [ chr(i) for i in range(48,  58) ]
SEEDS += [ chr(i) for i in range(65,  91) ]
SEEDS += [ chr(i) for i in range(97, 123) ]

# 创建指定的多个路径
def make_dir(path_list, mode=0755):
    if type(path_list) == type(''): path_list = [path_list]
    for path in path_list:
        if os.path.exists(path): continue
        recursion_make_dir(path, mode)
    return True

# 递归创建路径
def recursion_make_dir(path, mode=0755):
    if path[0] != '/': return False
    path_list = os.path.realpath(path).split('/')[1:]
    path_full = ''
    for i in path_list:
        path_full += '/' + i
        if os.path.exists(path_full): continue
        os.mkdir(path_full, mode)
    return True

# 生成随机字符串
def get_random_string(str_len=5) :
    return ''.join(random.sample(SEEDS, str_len))


def validate_key(request):
    """
    安全认证：查看客户端key和服务器端key是否相同
    """
    auth_key = settings.AUTH_KEY
    auth_string = request.GET.get('auth', '')
    auth_string_server = hashlib.md5('%s-%s' % (auth_key, datetime.datetime.now().strftime("%Y%m%d"))).hexdigest()
    return True if auth_string == auth_string_server else False

def get_auth_key():
    auth_key = settings.AUTH_KEY
    return hashlib.md5('%s-%s' % (auth_key, datetime.datetime.now().strftime("%Y%m%d"))).hexdigest()
