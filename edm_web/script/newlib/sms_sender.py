# -*- coding: utf-8 -*-
#
import sys
import urllib2, hashlib

from urllib import urlencode

############################################################
# 公共对象


############################################################
# 九天企信王接口 (http://www..sms9.net)

import time
class JiuTian(object) :
    api_base_url = "http://admin.sms9.net/houtai/"
    api_userid   = None
    api_passwd   = None
    api_channel  = None
    timestamp    = None

    # 错误代码说明
    err_desc = {
        '-1' : 'param error',
        '-2' : 'userid or password invalid',
        '-3' : 'channel id invalid',
        '-4' : 'mobile number invalid',
        '-5' : 'message content error',
        '-6' : 'the balance on your account is insufficient',
        '-7' : 'bind ip error',
        '-8' : 'not found signature',
        '-9' : 'signature invalid',
        '-10': 'channel suspended',
        '-11': 'the specifies time prohibit send',
        '-12': 'timestamp invalid',
    }


    # 设置用户帐号
    def set_account(self, userid, passwd, channel='15589') :
        self.timestamp  = str(int(time.time()))

        # 设置用户ID
        self.api_userid = userid

        # 设置加密后的密码
        password = '%s_%s_topsky' % (passwd, self.timestamp)
        h = hashlib.md5()
        h.update(password)
        self.api_passwd = h.hexdigest()

        # 设置使用的通道（'1773': 行业通道）
        self.api_channel = channel
        return


    # 接口调用方法
    def _call_api(self, phrase) :
        # 组合接口地址
        joinchar  = '&' if phrase.find('?') > -1 else '?'
        url = "%s%s%spassword=%s&timestamp=%s" % (
            self.api_base_url,
            phrase,
            joinchar,
            self.api_passwd,
            self.timestamp
        )
        #return url

        # 取得接口信息
        f = urllib2.urlopen(url)
        raw = f.read()
        f.close()
        return raw.strip()


    # 获取帐号状态
    def get_account_status(self) :
        phrase = "sms_ye.php?userid=%s" % self.api_userid
        result = self._call_api(phrase)

        # 分解返回数据
        (status, value) = result.split(':')
        status = status.strip()
        value  = value.strip()

        # 返回余额
        if status == 'success' :
            balance = '%.2f RMB' % float(value)
            return balance, None

        # 错误处理
        if status == 'error' :
            print>>sys.stderr, '%s: %s' % (value, self.err_desc[value])
            return False

        # 其它情况处理
        print>>sys.stderr, 'unknown error (%s)' % result
        return False


    # 发送短信
    def send_sms(self, mobile, message) :
        # 转字符为 GBK 编码
        # message = unicode(message, 'utf8').encode('gbk', 'ignore')
        try:
            message = message.encode('gbk', 'ignore')
        except:
            message = message.decode('utf-8', 'ignore').encode('gbk', 'ignore')

        # 生成短语，调用接口
        phrase = "sms.php?cpid=%s&channelid=%s&tele=%s&%s" % (
            self.api_userid,
            self.api_channel,
            mobile,
            urlencode({'msg': message})
        )
        result = self._call_api(phrase)

        # 分解返回数据
        (status, value) = result.split(':')
        status = status.strip()
        value  = value.strip()

        # 发送成功处理
        if status == 'success' : return True

        # 发送失败处理
        if status == 'error' :
            raise Exception, '%s: %s' % (value, self.err_desc[value])

        # 其它情况处理
        raise Exception, 'unknown error (%s)' % result



############################################################
# 华唐短信接口 (http://www.ht3g.com)


class HuaTang(object) :
    api_base_url = "http://www.ht3g.com/htWS/"
    api_username = None
    api_password = None


    # 设置用户帐号
    def set_account(self, user, passwd) :
        self.api_username = user
        self.api_password = passwd
        return


    # 接口调用方法
    def _call_api(self, phrase) :
        # 组合接口地址
        joinchar = '?'
        if phrase.find('?') > -1 : joinchar = '&'
        url = "%s%s%sCorpID=%s&Pwd=%s" % (self.api_base_url, phrase, joinchar, self.api_username, self.api_password)

        # 取得接口信息
        f = urllib2.urlopen(url)
        raw = f.read()
        f.close()
        return raw.strip()


    # 获取帐号状态
    def get_account_status(self) :
        phrase = "SelSum.aspx"
        count  = self._call_api(phrase)

        # 判断返回结果
        if int(count) < 0 :
            err_desc = {'-1': 'account invalid', '-2': 'unknown error', '-3': 'password invalid'}
            print>>sys.stderr, "%s: %s" % (count, err_desc[count])
            return False
        return count, None


    # 发送短信
    def send_sms(self, mobile, message) :
        # 转字符为 GBK 编码
        message = unicode(message, 'utf8').encode('gbk', 'ignore')

        # 生成短语，调用接口
        phrase = "Send.aspx?Mobile=%s&%s" % (mobile, urlencode({'Content': message}))
        result = self._call_api(phrase)

        if result != '0' :
            err_desc = {
                '-1': 'account invalid', '-2': 'unknown error', '-3': 'password invalid', '-4': 'mobile number error',
                '-5': 'insufficient balance', '-7': 'not allow send same content to ' + mobile + ' within 10 hours'
            }
            raise Exception, "%s: %s" % (result, err_desc[result])
        return True


############################################################
# 八优短信接口 (http://www.c8686.com/)

class BaYou(object) :
    api_base_url = "http://sms.c8686.com/api/BayouSmsApiEx.aspx"
    api_username = None
    api_password = None


    # 设置用户帐号
    def set_account(self, user, passwd) :
        # MD5 加密密码
        m = hashlib.md5()
        m.update(passwd)

        # 设置类属性
        self.api_username = user
        self.api_password = m.hexdigest()


    # 接口调用方法
    def _call_api(self, phrase) :
        # 取得接口信息
        url = "%s?%s&username=%s&password=%s" % (self.api_base_url, phrase, self.api_username, self.api_password)
        f = urllib2.urlopen(url)
        raw = f.read()
        f.close()
        raw = raw.decode('gbk').encode('utf8', 'ignore')
        raw = raw.replace('encoding="gb2312"', 'encoding="utf-8"')

        # 解析XML
        import PubXML as XMLObject
        data = XMLObject.parse_xml_string(raw)

        # 判断是否出错
        if data['errorcode'] != '0' :
            print>>sys.stderr, "remote error[%s]: %s" % (data['errorcode'], data['errordescription'])
            return False

        return data


    # 获取帐号状态
    def get_account_status(self) :
        phrase = "func=getuserinfo"
        data   = self._call_api(phrase)
        if not data: return False
        return data['msgcount'], data['sendmsgcount']


    # 发送短信
    def send_sms(self, mobile, message) :
        # 转字符为 GBK 编码
        message = unicode(message, 'utf8').encode('gbk', 'ignore')

        # 生成调用短语
        phrase = "func=sendsms&extno=&mobiles=%s&%s"
        phrase = phrase % (mobile, urlencode({'message': message}))

        # 调用接口
        data = self._call_api(phrase)
        if not data: return False
        return data['msgcount']

if __name__ == "__main__":
    s = JiuTian()
    s.set_account(userid=2685, passwd='`1qaz2wsx?', channel=1773)
    msg = u'lw　短信测试'
    print s.send_sms('18924664854', msg)
