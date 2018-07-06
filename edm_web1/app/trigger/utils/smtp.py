# -*- coding: utf-8 -*-

import smtplib

#############################################
# 账号密码发送邮件
def smtpSendEmail(host=None, port=25, account=None, password=None, sender=None, receivers=None, message=None):
    try:
        s = smtplib.SMTP()
        s.connect(host, port)    # 25 为 SMTP 端口号
        # s = smtplib.SMTP(host, port)
        code, msg = s.login(account, password)
        if not (200 <= code <= 299):
            return code, msg
        s.sendmail(sender, receivers, message)
        s.quit()
        code, msg = 250, 'ok'
    except smtplib.SMTPException:
        code, msg = -1, u"Unable to send mail!"
    except BaseException as e:
        code, msg = -1, repr(e)
    return code, msg
