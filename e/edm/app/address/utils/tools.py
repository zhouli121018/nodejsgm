#coding=utf-8
import time

# 保存错误地址
def save_error_addr(fw, addr):
    fw.write(u'{}\r\n'.format(addr))
    return

def handleSex(sex):
    if sex in (u'男', u'M', u'male', u'm', u'Male'):
        sex = 'M'
    elif sex in (u'女', u'F', u'female', u'f', 'Female'):
        sex = 'F'
    else:
        sex = ''
    return sex


def hanfBirthday(birthday):
    flag = False
    for type in ["%Y/%m/%d", "%Y-%m-%d", "%Y%m%d"]:
        tmp = formatBirthday(birthday, type)
        if tmp is not None:
            birthday = tmp
            flag = True
            break
    if not flag:
        return ''
    return birthday


def formatBirthday(birthday, type="%Y/%m/%d"):
    try:
        birthday = time.strptime(birthday, type)
        birthday = time.strftime("%Y-%m-%d", birthday)
    except:
        birthday = None
    return birthday