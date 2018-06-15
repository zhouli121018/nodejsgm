#coding=utf-8

import random
from lib.sms_sender import JiuTian
from app.core.models import Prefs
from django.conf import settings

EXPIRE_TIME = 10 * 60
num = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

def generate_code(bits=6):
    return "".join([num[random.randint(0, len(num) - 1)] for i in range(bits)])

def sms(mobile):
    sms_code = generate_code()
    content = u'尊敬的用户：您正在U-Mail注册账号，验证码为：{}'.format(sms_code)
    code, msg = -1, ''
    # 重试3次
    for i in range(3):
        try:
            j = JiuTian()
            j.set_account(userid=settings.JIUTIAN_ID, passwd=settings.JIUTIAN_PASSWD, channel=settings.JIUTIAN_CHANNEL)
            j.send_sms(mobile, content)
            code, msg = 250, sms_code
        except:
            code, msg = -1, ''
        if code == 250:
            break
    return code, msg