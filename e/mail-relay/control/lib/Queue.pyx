#!/usr/local/u-mail/app/engine/bin/python
#-*-coding:utf8-*-
#

import os
import time
import json
import shutil

import Core
import Common

############################################################
#
# task_queue:router
#   IDXXXXXXXXXXXXX-00000
#   IDYYYYYYYYYYYYY-00000
# task_queue:postman
#   IDZZZZZZZZZZZZZ-11111
# task_queue:forward
#   IDZZZZZZZZZZZZZ-22222
#
# task_lock:maillist
#   IDZZZZZZZZZZZZZ-33333
#
# task_data:mail (hash)
#   IDXXXXXXXXXXXXX-00000
#       {'field1': 'value1', 'field2': 'value2', ...}
#   IDYYYYYYYYYYYYY-00000
#       {'field1': 'value1', 'field2': 'value2', ...}
#   IDZZZZZZZZZZZZZ-11111
#       {'field1': 'value1', 'field2': 'value2', ...}
#   IDZZZZZZZZZZZZZ-22222
#       {'field1': 'value1', 'field2': 'value2', ...}
#   IDZZZZZZZZZZZZZ-33333
#       {'field1': 'value1', 'field2': 'value2', ...}
#

############################################################
# 公共数据

_ALLOW_QUEUE_ALIAS  = [
    'router',  'postman',   'smtp',   'dkim',   'incheck',  'outcheck', 'maillist',
    'forward', 'review',
    'reply',   'smsnotice', 'impush', 'recall', 'ldapsync', 'popmail',  'delete',
    'restore', 'smtp_delete'
]

############################################################
# 公共操作

# 检测指定的 Redis key 是否存在
def check_redis_key_exist(keyname) :
    return Common.dbRedis.exists(keyname)

# 清除 Redis 中的缓存数据
def clear_redis_cache() :
    for keyname in Common.dbRedis.keys("cache_*") :
        Common.dbRedis.delete(keyname)
    return

# 创建指定文件的副本
def create_file_copy(src_file, main_id = None) :
    savepath = os.path.dirname(src_file)
    task_id  = generate_task_id(main_id)
    dst_file = os.path.join(savepath, task_id)
    shutil.copy(src_file, dst_file)
    return task_id, dst_file

# 创建指定的任务文件
def create_task_file(queue_alias, maildata, main_id = None) :
    task_id  = generate_task_id(main_id)
    savepath = get_queue_cache(queue_alias)
    filepath = os.path.join(savepath, task_id)
    with open(filepath, 'w') as f :
        f.write(maildata)
        f.close()
    return task_id, filepath

# 添加 SMTP 任务队列
def add_smtp_task(task_main_id, filepath, recipients, base_data) :
    queue = TaskQueue('smtp')

    # 对收件人按域名进行分组
    domain_group = {}
    for _recipient in recipients :
        _domain = _recipient.split('@')[1]
        if _domain not in domain_group :
            domain_group[_domain] = []
        domain_group[_domain].append(_recipient)

    # 将各组收件人依次添加至 SMTP 任务队列
    log_list = []
    for _domain, _recipients in domain_group.items() :

        # 创建文件副本
        _task_id, _filepath = create_file_copy(filepath, task_main_id)

        # 分析子任务ID，生成日志数据
        _sub_id = parse_task_sub_id(_task_id)
        log_list.append((_sub_id, _recipients))

        # 生成任务数据
        _task_data = base_data
        _task_data['recipients'] = _recipients

        # 添加任务至队列
        queue.add_task_to_queue(_task_id, _task_data, _filepath)
    return log_list


############################################################
# Redis键名、缓存数据目录名获取操作

# 取得指定队列的 Redis 键名
def get_queue_key(queue_alias) :
    queue_alias = queue_alias.lower()
    key_name = 'task_queue:' + queue_alias
    return key_name

# 取得指定队列任务锁的 Redis 键名
def get_lock_key(queue_alias) :
    queue_alias = queue_alias.lower()
    key_name = 'task_lock:' + queue_alias
    return key_name

# 取得指定队列的数据存储 Redis 键名
def get_data_key(queue_alias) :
    queue_alias = queue_alias.lower()
    key_name = 'task_data:' + queue_alias
    return key_name

# 取得指定队列的文件缓存目录名称
def get_queue_cache(queue_alias) :
    queue_alias = queue_alias.lower()
    if queue_alias == 'lost' :
        path_name = 'lostmail'
    else :
        path_name = 'cache_' + queue_alias
    return os.path.join(Common.APP_DATA_ROOT, path_name)

# 取得指定队列的数据目录名称
def get_queue_data(queue_alias) :
    queue_alias = queue_alias.lower()
    if queue_alias == 'lost' :
        path_name = 'lostmail'
    else :
        path_name = 'data_' + queue_alias
    return os.path.join(Common.APP_DATA_ROOT, path_name)


############################################################
# 触发器操作

# 取得指定触发器的 Redis 键名
def get_trigger_key(trigger_alias) :
    trigger_alias = trigger_alias.lower()
    key_name = 'task_trigger:' + trigger_alias
    return key_name

# 检测指定的触发器是否存在
def check_trigger_key(trigger_alias) :
    key_name = get_trigger_key(trigger_alias)
    return Common.dbRedis.exists(key_name)

# 创建指定的触发器
def create_trigger(trigger_alias) :
    key_name = get_trigger_key(trigger_alias)
    return Common.dbRedis.set(key_name, 'run')

# 清除指定的触发器
def clear_trigger(trigger_alias) :
    key_name = get_trigger_key(trigger_alias)
    Common.dbRedis.delete(key_name)
    return True


############################################################
# 任务ID操作

# 生成完整的任务ID
def generate_task_id(main_id = None, sub_id = None) :
    if main_id is None : main_id = generate_task_main_id()
    if sub_id  is None : sub_id  = generate_task_sub_id()
    task_id = main_id + '-' + sub_id
    return task_id

# 生成任务主ID
def generate_task_main_id() :
    #main_id = time.strftime("%Y%m%d%H%M%S") + Common.get_random_string(5)
    main_id = str(time.time())[:10] + Common.get_random_string(5)
    return main_id

# 生成任务子ID
def generate_task_sub_id() :
    return Common.get_random_string(5)

# 从完整的任务ID中解析出任务主ID
def parse_task_main_id(task_id) :
    return task_id.split('-')[0]

# 从完整的任务ID中解析出任务子ID
def parse_task_sub_id(task_id) :
    return task_id.split('-')[1]


############################################################
# 任务队列操作类

class _TaskData:

    def __init__(self, queue_alias) :
        self.queue_alias = queue_alias
        self.data_key   = get_data_key(queue_alias)

    # 设置任务数据
    def set_task_data(self, task_id, data):
        data = json.dumps(data)
        return Common.dbRedis.hset(self.data_key, task_id, data)

    # 设置任务的原始任务数据
    def set_raw_task_data(self, task_id, data):
        return Common.dbRedis.hset(self.data_key, task_id, data)

    # 检测指定的任务数据是否存在
    def check_task_exist(self, task_id):
        return Common.dbRedis.hexists(self.data_key, task_id)

    # 取得指定任务处理后的任务数据
    def get_task_data(self, task_id):
        data = Common.dbRedis.hget(self.data_key, task_id)
        if data is None : return
        data = json.loads(data)
        return data

    # 取得指定任务的原始任务数据
    def get_raw_task_data(self, task_id):
        data = Common.dbRedis.hget(self.data_key, task_id)
        return data

    # 清除指定任务的任务数据
    def clear_task_data(self, task_id):
        return Common.dbRedis.hdel(self.data_key, task_id)

    # 取得指定任务的元数据
    def get_task_meta(self, task_id, key):
        data = self.get_task_data(task_id)
        if key not in data : return
        return data[key]

    # 设置指定任务的元数据
    def set_task_meta(self, task_id, new_data):
        save_data = self.get_task_data(task_id)
        for k, v in new_data.items() :
            save_data[k] = v
        return self.set_task_data(task_id, save_data)


class TaskQueue(_TaskData):

    def __init__(self, queue_alias):
        # 队列别名检测
        if queue_alias not in _ALLOW_QUEUE_ALIAS :
            raise ValueError, "unknown queue alias: %s" % queue_alias

        # 初始化 _TaskData
        _TaskData.__init__(self, queue_alias)

        # 设置内部属性
        self.queue_alias = queue_alias
        self.queue_key   = get_queue_key(queue_alias)
        self.lock_key    = get_lock_key(queue_alias)
        self.cache_name  = get_queue_cache(queue_alias)


    ############################################################
    # 队列任务操作

    # 添加任务至任务队列
    def add_task_to_queue(self, task_id, data = None, filepath = None) :

        # 处理任务文件
        if filepath is not None :
            src_path = os.path.realpath(filepath)
            dst_path = os.path.join(self.cache_name, task_id)
            if not os.path.exists(src_path) :
                raise Exception, 'not found task file (%s: %s)' % (task_id, src_path)
            shutil.move(src_path, dst_path)

        # 检测或设置任务数据
        if data is None :
            if not self.check_task_exist(task_id) :
                raise Exception, 'not found task data (%s)' % task_id
        else :
            self.set_task_data(task_id, data)

        # 添加至任务队列
        Common.dbRedis.rpush(self.queue_key, task_id)
        return True

    # 从队列中取出一个任务
    def get_task_from_queue(self) :
        task_id = Common.dbRedis.lpop(self.queue_key)
        if task_id   is None : return

        # 取出任务数据并返回
        task_data = self.get_task_data(task_id)
        if task_data is None : return

        # 设置任务锁
        self.acquire_task_lock(task_id)
        return task_id, task_data

    # 将任务退回至队列
    def back_task_to_queue(self, task_id):

        # 清除任务锁
        self.release_task_lock(task_id)

        # 将任务追加至队列
        return Common.dbRedis.rpush(self.queue_key, task_id)

    # 清除任务
    def clear_task(self, task_id):

        # 删除任务文件
        filepath = os.path.join(self.cache_name, task_id)
        if os.path.exists(filepath) :
            os.unlink(filepath)

        # 清除任务数据
        self.clear_task_data(task_id)

        # 释放任务执行锁
        self.release_task_lock(task_id)
        return True

    # 清空当前队列
    def clear_all_task(self):
        while True :
            task_id = Common.dbRedis.lpop(self.queue_key)
            if task_id is None : break
            self.clear_task(task_id)
        return True


    ############################################################
    # 任务执行锁操作

    # 申请任务执行锁
    def acquire_task_lock(self, task_id):
        return Common.dbRedis.sadd(self.lock_key, task_id)

    # 检测任务执行锁
    def check_task_lock(self, task_id):
        return Common.dbRedis.sismember(self.lock_key, task_id)

    # 释放任务执行锁
    def release_task_lock(self, task_id):
        return Common.dbRedis.srem(self.lock_key, task_id)

    # 清除所有执行锁
    def clear_task_lock(self):
        Common.dbRedis.delete(self.lock_key)

