#!/usr/local/u-mail/app/engine/bin/python
#-*-coding:utf8-*-
#

import os
import sys
import logging
import logging.handlers

############################################################
# 全局变量

program_name = None
date_format  = "%Y-%m-%d %H:%M:%S"

############################################################


# 初始化日志记录器
def init_logger(name, logfile=None, logerr=None, level=logging.INFO, file_owner=None) :
    globals()['program_name']  = name

    # 重设已有句柄的输出格式
    if name :
        for hdr in logging.root.handlers :
            hdr.setFormatter(logging.Formatter(_get_log_formatter(), date_format))

    # 设置日志文件句柄
    if logfile : logging.root.addHandler(_create_file_handle(level, logfile, file_owner=file_owner))
    if logerr  : logging.root.addHandler(_create_file_handle(logging.ERROR, logerr, file_owner=file_owner))
    return True


# 移除屏幕输出
def remove_screen_output() :
    for hdr in logging.root.handlers :
        if isinstance(hdr, logging.StreamHandler) :
            logging.root.removeHandler(hdr)
            break
    return


# 重定向系统标准输出
def redirect_stdout() :
    sys.stdout = StreamToLogger(logging, logging.INFO)
    sys.stderr = StreamToLogger(logging, logging.ERROR)


# 外调日志输出函数
def outinfo(msg)  : outlog(msg, logging.INFO)
def outerror(msg) : outlog(msg, logging.ERROR)
def outwarn(msg)  : outlog(msg, logging.WARNING)
def outdebug(msg) : outlog(msg, logging.DEBUG)
def outlog(msg, level) :
    logging.log(level, msg)


#
#  创建日志记录对象相关操作
#


# 创建文件类型的记录对象
def _create_file_handle(level, filename, param=None, file_owner=None) :
    if param is None : param = {}
    log_param = {
        'filename'    : filename,
        'when'        : ('when'         in param) and param['when']         or 'midnight',
        'interval'    : ('interval'     in param) and param['interval']     or 1,
        'backup_count': ('backup_count' in param) and param['backup_count'] or 7,
        'file_owner'  : file_owner,
    }
    handler = TimedRotatingFileHandler(**log_param)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(_get_log_formatter(), date_format))
    return handler


# 获取日志格式对象
def _get_log_formatter() :
    if program_name is None :
        fmt = '%(asctime)s [%(levelname)s]: %(message)s'
    else :
        fmt = '%(asctime)s ' + program_name + '[%(levelname)s]: %(message)s'
    return fmt



############################################################
# 类对象


class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   """
   def __init__(self, logger, log_level=logging.INFO):
      self.logger  = logger
      self.level   = log_level
      self.linebuf = ''

   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.level, line.rstrip())


# 重写 TimedRotatingFileHandler 中的 doRollover 方法
class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler) :
    file_uid = None
    file_gid = None

    def init_file_owner(self, uid, gid=None):
        """
        初始化日志文件的属主信息
        @param uid: 文件属主的 UID
        @param gid: 文件属主的 GID
        """

        self.file_uid = uid
        self.file_gid = uid if gid is None else gid

    def set_file_owner(self):
        """
        设置文件的属主信息
        """

        if os.getuid()   != 0    : return   # 如果不是以 root 用户运行，则返回
        if self.file_uid is None : return   # 如果没有设置文件属主信息，则返回
        #os.chown(self.baseFilename, self.file_uid, self.file_gid)


    ############################################################
    # 改写原方法


    def __init__(self, filename, when='h', interval=1, backup_count=0, encoding=None, delay=False, utc=False, file_owner=None):

        # 初始化文件属主信息
        if file_owner is not None :
            self.init_file_owner(file_owner[0], file_owner[1])

        # 调用父类的 __init__ 方法
        super(TimedRotatingFileHandler, self).__init__(filename, when, interval, backup_count, encoding, delay, utc)

        # 设置文件属主
        self.set_file_owner()


    def doRollover(self) :

        # 调用父类的 doRollover 方法
        super(TimedRotatingFileHandler, self).doRollover()

        # 设置文件属主
        self.set_file_owner()


############################################################
# 执行操作

# 设置日志模块基本配置
logging.basicConfig(
    format  = _get_log_formatter(),
    datefmt = date_format,
    level   = logging.DEBUG
)


