# -*- coding: utf-8 -*-
#
""" 首先获取锁，然后执行操作， 最后释放锁；
使用WATCH命令来监控被频繁访问的键可能会引起性能问题；
setex 具有基本的加锁功能，但功能不完整，不具备分布式锁常见的一些高级特性；
1. 使用watch < 2. 使用锁 < 3. 使用细粒度锁（分解成唯一标识）

乐观锁：
获取锁（acquire）对数据进行排他性访问的能力
"""
import time
import uuid
import json
from math import ceil
from redis.exceptions import WatchError


def simple_acquire_lock(redis, key, expire_time=4000):
    if redis.exists(key):
        return True
    ( redis.pipeline()
      .set(key, 1)
      .expire(key, expire_time)
      .execute() )
    return False

def simple_realese_lock(redis, key):
    redis.delete(key)


#####################################
# 分布式锁
# 多进程操作锁， 单进程操作锁直接操作程序锁即可
def acquire_lock(redis, lockname, acquire_timeout=10, lock_timeout=30):
    """
    :param redis:
    :param lockname: 锁key
    :param timeout: 超时时间
    :return: identifier 标识, 用于解锁
    """
    identifier = str(uuid.uuid4())  # 128位随机标识符
    lock_timeout = int(ceil(lock_timeout))
    end = time.time() + acquire_timeout
    while time.time()<end:
        if redis.set(lockname, identifier, ex=lock_timeout, nx=True):
            return identifier
        # if redis.setnx(lockname, identifier): # 尝试获得锁
        #     redis.expire(lockname, lock_timeout)
        #     return identifier
        # elif not redis.ttl(lockname):
        #     redis.expire(lockname, lock_timeout)
        time.sleep(0.001)
    return None

def release_lock(redis, lockname, identifier):
    """
    :param redis:
    :param lockname:
    :param identifier:
    :return:
    """
    p = redis.pipeline()
    while True:
        try:
            p.watch(lockname)
            if p.get(lockname) == identifier: # 检查进程是否仍持有锁
                # 释放锁
                p.multi()
                p.delete(lockname)
                p.execute()
                return True
            p.unwatch(lockname)
            break
        except WatchError:
            pass # 有客户端修改了锁，重试
    return False # 进程已失去锁


#####################################
# 计数信号量锁 ( 信号量是不公平（unfair）的)
# 应用场景： 限制每个账号最多只能有5个进程同时访问市场
def acquire_semaphore(redis, semname, limit, timeout=10):
    """
    :param redis:
    :param semname:
    :param limit:
    :param timeout:
    :return: identifier
    """
    identifier = str(uuid.uuid4())
    now = time.time()
    p = redis.pipeline()
    p.zremrangebyscore(semname, '-inf', now-timeout) # 清理过期的信号量持有者
    p.zadd(semname, identifier, now) # 尝试获取信号量
    p.zrank(semname, identifier)
    if p.execute()[-1] < limit: # 检查是否成功取得了信号量
        return identifier
    redis.zrem(semname, identifier) # 后去信号量失败， 删除之前的信号量
    return None

def release_semaphore(redis, semname, identifier):
    return redis.zrem(semname, identifier)

#####################################
# 公平锁


#####################################
# 延迟任务队列 Zset queue
def execute_later(redis, queue, delayqueue, name, args, delay=0):
    """
    :param redis:  唯一标识符
    :param queue:  处理任务队列的名称
    :param delayqueue: 延迟队列
    :param name: 处理任务的回调函数的名字
    :param args: 传给回调函数的参数
    :param delay: 延迟时间
    :return:
    """
    identifier = str(uuid.uuid4())
    # 准备需要入队的任务
    item = json.dumps([identifier, queue, name, args])
    if delay>0:
        redis.zadd(delayqueue, item, time.time()+delay)
    else:
        redis.lpush(queue, item)
    return identifier

# 从延迟队列获取执行任务
def poll_queue(redis):
    delayqueue = "delayed:"
    while True:
        item = redis.zrange(delayqueue, 0, 0, withscores=True)
        if not item or item[0][1]>time.time():
            time.sleep(0.01)
            continue
        item = time[0][0]
        identifier, queue, name, args = json.loads(item)
        lockname = ":lock:"+identifier
        locked = acquire_lock(redis, lockname)
        if not locked: continue

        if redis.zrem(delayqueue, item):
            redis.lpush(queue, item)
        release_lock(redis, lockname, locked)


#####################################
# 优先级任务队列
# 高优先级、中等优先级、低优先级
# queues = ["high-delayed", "high", "medium-delayed", "medium", "low-delayed", "low"]
# redis.brpop(queues, timeout=5)

