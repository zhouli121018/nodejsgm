# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText

class MailSender(object):
    def set_message(self, sender, receiver, subject, html_text):
        m = MIMEText(html_text, _subtype='html',_charset='gb2312')
        m['From'] = sender
        m['To'] = receiver
        m['Subject'] = subject

        return m.as_string()

    def send_email(self, host, port, sender, password, receiver, subject, message):
        try:
            message = self.set_message(sender, receiver, subject, message)
            s = smtplib.SMTP(host, port)

            code, msg = s.login(sender, password)
            if not (200 <= code <= 299):
                return code, msg

            s.sendmail(sender, receiver, message)
            s.quit()
            return 250, 'ok'
        except smtplib.SMTPResponseException as e:
            code, msg = e.smtp_code, e.smtp_error
            return code, msg
        except smtplib.SMTPRecipientsRefused as e:
            senderrs = e.recipients
            code, msg = senderrs[receiver]
            return code, msg
        except BaseException as e:
            code, msg = -1, repr(e)
            return code, msg

if __name__ == "__main__":
    s = MailSender()
    print s.send_email('mail2.comingchina.com', 25, 'postmaster@comingchina.com', 'mmglsmd`1qaz', '1351722462@qq.com', u'测试邮件', u'这是一封测试邮件')

