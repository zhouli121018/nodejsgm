# -*- coding: utf-8 -*-

import hashlib
import time
import json
import requests

class Client(object):

    def __init__(self, url):
        self.key = 'abcc7aee-7824-11e7-b733-b8aeedeaf1f5'
        self.key_name = 'auth-key'
        self.asset_api = url


    def auth_key(self):
        """
        接口认证
        """
        ha = hashlib.md5(self.key.encode('utf-8'))      # 用self.key 做加密盐
        time_span = time.time()
        ha.update(bytes("%s|%f" % (self.key, time_span)))
        encryption = ha.hexdigest()
        result = "%s|%f" % (encryption, time_span)
        return {self.key_name: result}

    def get_asset(self):
        """
        post方式向街口提交资产信息
        """
        headers = {}
        headers.update(self.auth_key())
        r = requests.get(
            url=self.asset_api,
            headers=headers,
        )
        if r.status_code == 200:
            json_str =  r.text
            j = json.loads(json_str)
            # import pprint
            # pprint.pprint(j)
            return r.status_code, j
        else:
            return r.status_code, r.text


if __name__ == "__main__":
    url = 'http://admin.mailrelay.cn/api_search/mail_status/?mail_to_list={}&mail_from={}&search_date={}&hour={}'.format(
        'jackson.yang@tuv.com', '', '', ''
    )
    status_code, response_text = Client(url).get_asset()
    print status_code
    import pprint
    pprint.pprint(response_text)