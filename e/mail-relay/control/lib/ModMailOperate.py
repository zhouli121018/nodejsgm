# !/usr/local/u-mail/app/engine/bin/python
#-*-coding:utf8-*-
#

import re
import email.header
from tempfile import TemporaryFile

import chardet


############################################################
# 公共数据

SEEDS = [chr(i) for i in range(48, 58)]
SEEDS += [chr(i) for i in range(65, 91)]
SEEDS += [chr(i) for i in range(97, 123)]

############################################################
# 自定义异常


# 取得指定邮件的头信息 (邮件文件)
def get_mail_header_by_file(mailpath):
    lines = []
    fp = open(mailpath, 'r')
    while True:
        line = fp.readline()
        if line.rstrip() == '':
            fp.close()
            break
        lines.append(line)
    return ''.join(lines)


# 取得指定邮件的头信息 (邮件内容)
def get_mail_header_by_data(maildata):
    header = []
    break_flag = False
    for x in xrange(len(maildata)):
        if maildata[x] == '\r': continue
        if maildata[x] != '\n':
            break_flag = False
            header.append(maildata[x])
            continue
        if break_flag: break
        break_flag = True
        header.append('\n')
    header.append('\n')
    return ''.join(header)


# 替换指定邮件的邮件头
def replace_mail_header(mailpath, header):
    # 创建临时文件，写入新的邮件头
    tfp = TemporaryFile()
    tfp.write(header)

    # 将原邮件的内容部分写入临时文件
    is_found = False
    rfp = open(mailpath, 'rb')
    for line in rfp:
        if is_found:
            tfp.write(line)
            continue
        if line.rstrip() == '': is_found = True
    rfp.close()

    # 使用临时文件的内容替换原文件
    wfp = open(mailpath, 'wb')
    tfp.seek(0)
    while True:
        buf = tfp.read(8192)
        if not buf: break
        wfp.write(buf)
    tfp.close()
    wfp.close()


# 取得指定邮件的主题
def get_mail_subject(mail_path='', mail_data='', default=None):
    # 创建邮件对象
    if mail_data:
        mail_obj = email.message_from_string(mail_data)
    else:
        mail_obj = email.message_from_file(open(mail_path))
    return get_header_value(mail_obj, 'Subject', default)


# 取得指定头解码后的内容
def get_header_value(header, field, default=None):
    field = field.lower()

    # subject
    if field in ['subject']:
        raw_value = header.get(field, None)
        if raw_value is None: return default
        return decode_header_string(raw_value)[0]

    # from, sender
    elif field in ['from', 'sender']:

        # 取得原始字符串
        raw_value = header.get(field, None)
        if raw_value is None: return default

        # 处理地址
        addresses = list(email.utils.parseaddr(raw_value))
        addresses[0] = decode_header_string(addresses[0])[0]
        addresses[1] = '<%s>' % addresses[1]
        return addresses[1] if addresses[0] == '' else ' '.join(addresses)

    # to, cc
    elif field in ['to', 'cc', 'bcc']:

        # 取得原始数据列表
        raw_value = header.get_all(field, None)
        if raw_value is None: return default

        # 处理地址列表
        raw_list = email.utils.getaddresses(raw_value)
        new_list = []
        for addresses in raw_list:
            addresses = list(addresses)
            addresses[0] = decode_header_string(addresses[0])[0]
            addresses[1] = '<%s>' % addresses[1]
            new_list.append(addresses[1] if addresses[0] == '' else ' '.join(addresses))
        return ', '.join(new_list)

    # date
    elif field == 'date':
        _date = header.get('Date', None)
        if _date is None: return default
        _date = _date.decode('latin-1').encode("utf-8")
        return _date

    # 其它
    return header.get(field, default)


# 按指定顺序尝试获取邮件头的值（只要有数据则返回）
def get_header_value_of_order(header, sequence, default=None):
    for key in sequence:
        val = header.get(key, None)
        if val is not None: return val
    return default


# 解码邮件主题
def decode_header_string(raw_string):
    if raw_string is None: return "", 'utf-8'

    # 对原始字符串进行兼容性处理，此处理只能针对 BASE64 编码，不能对 QUOTED-PRINTABLE
    # 编码进行操作
    if ('?B?' in raw_string or '?b?' in raw_string) and ('?==?' in raw_string):
        for _item in re.findall(r"(=\?.*?\?=)\S", raw_string):
            raw_string = raw_string.replace(_item, _item + ' ')

    # 对邮件主题进行初步解码
    try:
        parts = email.header.decode_header(raw_string)
    except:
        return raw_string, 'utf-8'

    # 处理邮件主题
    full_str = ''
    charset = None
    for part in parts:

        # 判断当前部分的字符编码
        if part[1]:
            _charset = 'gbk' if part[1] == 'gb2312' else part[1]
            if part[1] == '136': _charset = 'ascii'
        else:
            _charset = chardet.detect(part[0])['encoding']
        if charset is None: charset = _charset

        # 将当前部分追加至主题中
        if _charset is None:
            part_str = part[0].encode('utf-8', 'ignore')
        elif _charset == 'utf-8':
            part_str = part[0]
        else:
            part_str = part[0].decode(_charset, 'ignore').encode('utf-8', 'ignore')
        full_str += ' ' + part_str
    return full_str.lstrip(), charset


