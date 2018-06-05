# -*- coding: utf-8 -*-
#

import os

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