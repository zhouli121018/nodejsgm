#!/usr/bin/env python
# -*- coding:utf-8 -*-
#

import urllib

class Ctasd(object) :

    def __init__(self, host, port, key=None) :
        self.server_host = host
        self.server_port = port
        self.license_key = key
        self.operate_map = {
            'getStatus'    : 'GetStatus',
            'checkMailFile': 'ClassifyMessage_File',
            'checkMailData': 'ClassifyMessage_Inline',
            'validateRule' : 'ValidateCustomRules',
            'getRuleList'  : 'GetRulesList',
            'getServices'  : 'GetServices',
            'getRuleDefinitionList': 'GetCTRulesDefinitionList',
            'getRuleDefinition'    : 'GetCTRuleDefinition',
        }

    ############################################################
    # 入站垃圾邮件检测操作

    def check_in_mail_file(self, filepath, senderip=None, mailfrom=None):
        """
        检测指定的入站邮件文件是否为垃圾邮件
        :param filepath: 邮件文件保存路径
        :param senderip: 邮件发送者IP
        :param mailfrom: 邮件发送者地址
        """

        header = self._build_pub_header()
        header.append('X-CTCH-FileName:' + filepath)
        if senderip :
            header.append('X-CTCH-SenderIP:' + senderip)
        if mailfrom :
            header.append('X-CTCH-MailFrom:' + mailfrom)
        result = self._do('checkMailFile', header)
        return result


    def check_in_mail_data(self, maildata, senderip=None, mailfrom=None):
        """
        检测指定的入站邮件数据是否为垃圾邮件
        :param maildata: 邮件内容
        :param senderip: 邮件发送者IP
        :param mailfrom: 邮件发送者地址
        """

        header = self._build_pub_header()
        if senderip :
            header.append('X-CTCH-SenderIP:' + senderip)
        if mailfrom :
            header.append('X-CTCH-MailFrom:' + mailfrom)
        result = self._do('checkMailData', header, maildata)
        return result


    ############################################################
    # 出站垃圾邮件检测操作

    def check_out_mail_file(self, filepath, senderid, rcptcnt=None):
        """
        检测指定的出站邮件文件是否为垃圾邮件
        @param filepath: 邮件文件保存路径
        @param senderid: 邮件发送者地址
        @param rcptcnt: 收件人数量
        @rtype : dict
        """

        header = self._build_pub_header()
        header.append('X-CTCH-SenderID:' + senderid)
        header.append('X-CTCH-FileName:' + filepath)
        if rcptcnt :
            header.append('X-CTCH-RcptCount: %d' % rcptcnt)
        result = self._do('checkMailFile', header)
        return result


    def check_out_mail_data(self, maildata, senderid, rcptcnt=None):
        """
        检测指定的出站邮件数据是否为垃圾邮件
        @param maildata: 邮件内容
        @param senderid: 邮件发送者地址
        @param rcptcnt: 收件人数量
        @rtype : dict
        """

        header = self._build_pub_header()
        header.append('X-CTCH-SenderID:' + senderid)
        if rcptcnt :
            header.append('X-CTCH-RcptCount: %d' % rcptcnt)
        result = self._do('checkMailData', header, maildata)
        return result


    ############################################################
    # 邮件报告操作

    def report_fp(self, maildata, srv='spam'):
        """
        提交误判报告
        注：邮件头中必须包含有“X-CTCH-RefID”信息
        :param maildata: 邮件内容
        :param srv: 服务类型，“spam”：垃圾邮件，“vod”：病毒发送邮件，“outbound”：出站垃圾邮件
        """

        srv_list = {'spam': '1', 'vod': '2', 'outbound': '8'}
        srv_id   = srv_list[srv]

        header = self._build_pub_header()
        header.append('X-CTCH-Service:' + srv_id)
        result = self._do('reportFP', header, maildata)
        return result

    def report_fn(self, maildata, srv='spam'):
        """
        提交漏判报告
        注：邮件头中必须包含有“X-CTCH-RefID”信息
        :param maildata: 邮件内容
        :param srv: 服务类型，“spam”：垃圾邮件，“vod”：病毒发送邮件，“outbound”：出站垃圾邮件
        """

        srv_list = {'spam': '1', 'vod': '2', 'outbound': '8'}
        srv_id   = srv_list[srv]

        header = self._build_pub_header()
        header.append('X-CTCH-Service:' + srv_id)
        result = self._do('reportFN', header, maildata)
        return result


    ############################################################
    # 状态查询操作

    # 测试 ctasd 与数据中心的连接状态
    def get_status(self) :
        header = self._build_pub_header()
        result = self._do('getStatus', header)
        return result['X-CTCH-PVer']

    # 取得当前 ctasd 的服务信息
    def get_services(self):
        services = {1: 'anti-spam', 2: 'virus-protection', 4: 'url-filter', 8: 'outbound-spam'}

        # 获取服务ID
        header = self._build_pub_header()
        result = self._do('getServices', header)
        srv_id = int(result['X-CTCH-Services'])

        # 分解服务ID
        srv_list = []
        for i in [8, 4, 2, 1] :
            if srv_id < i : continue
            srv_list.append(services[i])
            srv_id -= i
        return srv_list


    ############################################################
    # 自定义规则操作

    # 取得所有规则列表
    def get_rule_list(self):
        header = self._build_pub_header()
        result = self._do('getRuleList', header)
        return result['X-CTCH-Rules'].split(',')

    # 取得 Commtouch 规则列表
    def get_rule_definition_list(self):
        header = self._build_pub_header()
        result = self._do('getRuleDefinitionList', header)
        return result['X-CTCH-Rules'].split(',')

    # 取得 Commtouch 规则信息
    def get_rule_definition(self, tag):
        header = self._build_pub_header()
        header.append('X-CTCH-RuleTag:' + tag)
        result = self._do('getRuleDefinition', header)
        return result['X-CTCH-Rule']

    # 验证自定义规则格式是否正确
    def validate_rule(self, path):
        header = self._build_pub_header()
        header.append('X-CTCH-Path:' + path)
        result = self._do('validateRule', header)
        return result


    ############################################################
    # 内部调用操作

    # 创建共用的头信息
    def _build_pub_header(self):
        header = ['X-CTCH-PVer:0000001']
        if self.license_key is not None :
            header.append('X-CTCH-Key:' + self.license_key)
        return header

    # 执行检测操作
    def _do(self, op, header, data=None):
        # 生成接口地址
        url = "http://%s:%s/ctasd/%s" % (self.server_host, self.server_port, self.operate_map[op])

        # 生成提交数据
        postdata = '\r\n'.join(header)
        if data is not None :
            postdata += '\r\n\r\n' + data

        # 向接口提交数据，并处理返回结果
        fp = urllib.urlopen(url, postdata)

        # 判断 HTTP 状态是否正常
        http_code = fp.getcode()
        if http_code != 200 :
            msg = "HTTP status exception (%s: %s)" % (http_code, fp.read().strip())
            raise Exception(msg)

        # 处理数据
        dat = {}
        raw = ''
        for line in fp :
            raw += line
            pos  = line.find(':')
            k = line[0:pos]
            v = line[pos + 1:]
            dat[k] = v.strip()
        return dat
