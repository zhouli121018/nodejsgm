# coding=utf-8
import math
import random
from django.http import Http404
from app.setting.utils.children import get_customer_child_obj
from app.statistics.configs import COLOR_20

def get_realcustomer_and_obj(request, user_id):
    subobj = None
    customer_id = request.user.id
    if user_id:
        service_obj = request.user.service()
        if service_obj.is_share_flag in('2', '3', '4'):
            raise Http404
        customer_id = user_id
        subobj = get_customer_child_obj(request, user_id)
    return customer_id, subobj


#################################################
def get_histogram_y_list(max_data):
    avg_data = int(math.ceil(float(max_data)/float(6)))
    histogram_y_list = [0]
    tmp = 0
    while True:
        tmp += avg_data
        if len(histogram_y_list) == 6:
            histogram_y_list.append(max_data)
            break
        else:
            histogram_y_list.append(tmp)
    return histogram_y_list


# 获取比例
def get_rate(element, total, round_num=2):
    if total:
        return "{}%".format(round( ( element*100.00/total ), round_num) )
    return '0%'

def get_width(element, total):
    if total:
        return "{}px".format(round( ( (element*100.00/total)*1.500 ), 5) )
    return '0px'

def split_ip_info(ip_info):
    if ip_info == u'N/A':
        return '', ''
    iplist = ip_info.split('|')
    country, area = iplist[1], ''
    if iplist[1] == u'中国':
        if iplist[2] in [u'香港', u'澳门']:
            area = u'广东'
        else:
            area = iplist[2]
    if country == u'保留':
        country = ''
    return country, area

def get_max_data(value):
    max_data = 6
    if 0< value <=100:
        max_data = get_max_data_add(value)
    elif 96< value <=960:
        max_data = get_max_data_add(int(str(int(value*1.1))[:-1]))*10
    elif value > 960:
        max_data = get_max_data_add(int(str(int(value*1.1))[:-2]))*100
    return max_data

def get_max_data_add(value):
    for i in range(10):
        if (value+i)%6 == 0:
            max_data = value + i
            break
    return max_data

def get_gfc_max_data(value):
    max_data = 10
    if 0< value <=100:
        max_data = get_gfc_max_data_add(value)
    elif 100< value <=999:
        max_data = get_gfc_max_data_add(int(str(int(value*1.1))[:-1]))*10
    elif value >= 1000:
        max_data = get_gfc_max_data_add(int(str(int(value*1.1))[:-2]))*100
    return max_data

def get_gfc_max_data_add(value):
    for i in range(11):
        if (value+i)%10 == 0:
            max_data = value + i
            break
    return max_data

def get_gec_random_color():
    res = "#"
    chars = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    for i in range(6):
        res += chars[int(math.ceil((random.random())*15))]
    return res


def get_domain_data(data=None):
    vals, count = {}, 0
    for email in data:
        count += 1
        domain = email[0].split("@")[-1].strip()
        if domain in vals:
            vals[domain] += 1
        else:
            vals.update({ domain: 1 })

    sortVals= sorted(vals.iteritems(), key=lambda d:d[1], reverse = True)[:20]
    datalist, labels  = [], []
    if len(sortVals) == 1:
        sortVals.append(('other', 0))
    bgcolor = COLOR_20[:len(sortVals)]
    for val in sortVals:
        datalist.append(val[1])
        labels.append('{}({}%)'.format(val[0], round(val[1] * 100.00 / count, 2) ))
    return {
        'datalist': datalist,
        'bgcolor': bgcolor,
        'labels': labels,
    }
