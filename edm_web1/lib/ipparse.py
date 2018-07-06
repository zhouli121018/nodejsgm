#coding=utf-8

def parse_login_area(ipinfo):
    iplist = ipinfo.split('|')
    if iplist[1] == u'中国':
        area1 = iplist[2]
        area2 =iplist[3] if iplist[3] else iplist[2]
    else:
        area1, area2 = u"国外", u"国外"
    return area1, area2

province_list = [u'上海', u'北京', u'天津', u'河北', u'山西', u'内蒙古',
                 u'辽宁', u'吉林', u'黑龙江', u'江苏', u'浙江', u'安徽',
                 u'福建', u'江西', u'山东', u'河南', u'湖北', u'湖南',
                 u'广东', u'广西', u'海南', u'重庆', u'四川', u'贵州',
                 u'云南', u'西藏', u'陕西', u'甘肃', u'青海', u'宁夏',
                 u'新疆', u'台湾', u'香港', u"澳门"]

def get_ip_detail(ipinfo, lang):
    if lang == "en-us":
        return get_ip_detail_en(ipinfo)
    else:
        return get_ip_detail_zh(ipinfo)

def get_ip_detail_en(ipinfo):
    if not ipinfo or ipinfo==u"N/A":
        return u"China", u"CN"
    iplist = ipinfo.split('|')
    if iplist[1] == u'中国':
        area = iplist[8] if iplist[8] else iplist[7]
        title = iplist[7] + ' ' + iplist[8]
    else:
        area = iplist[7]
        title = iplist[7] + ' ' + iplist[8]
    return area, title

def get_ip_detail_zh(ipinfo):
    if not ipinfo or ipinfo==u"N/A":
        return u"China", u"CN"
    iplist = ipinfo.split('|')
    if iplist[1] == u'中国':
        area = iplist[2] if iplist[2] else iplist[1]
        title = iplist[0] + ' ' + iplist[1] + ' ' + iplist[2] + ' ' + iplist[3] + ' ' + iplist[4] + ' ' + iplist[5] + ' '
    else:
        area = iplist[1]
        title = iplist[0] + ' ' + iplist[1] + ' ' + iplist[2] + ' ' + iplist[3] + ' ' + iplist[4] + ' ' + iplist[5] + ' '
    return area, title

def split_ip_info(ip_info):
    if ip_info == u'N/A':
        return '', ''
    iplist = ip_info.split('|')
    if iplist[1] == u'中国':
        area = iplist[2] if iplist[2] else iplist[1]
        title = iplist[0] + ' ' + iplist[1] + ' ' + iplist[2] + ' ' + iplist[3] + ' ' + iplist[4] + ' ' + iplist[
            5] + ' '
    else:
        area = iplist[1]
        title = iplist[0] + ' ' + iplist[1] + ' ' + iplist[2] + ' ' + iplist[3] + ' ' + iplist[4] + ' ' + iplist[
            5] + ' '
    return area, title

def split_ip_to_area_title(ip_info):
    if ip_info == u'N/A':
        return '', ''
    iplist = ip_info.split('|')
    if iplist[1] == u'中国':
        area = iplist[2] if iplist[2] else iplist[1]
        title = iplist[2] + ' ' + iplist[3] + ' ' + iplist[4] + ' ' + iplist[5] + ' '
    else:
        area = iplist[1]
        title = iplist[0] + ' ' + iplist[1] + ' ' + iplist[2] + ' ' + iplist[3] + ' ' + iplist[4] + ' ' + iplist[5] + ' '
    return area, title