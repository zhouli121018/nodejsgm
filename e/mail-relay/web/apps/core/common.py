# coding=utf8
import ipaddr
from apps.core.models import Customer, IpPool
from django.db.models import Count


def get_ip_list_from_net(net):
    """
    网段: net: '211.195.0.0/24'
    """
    try:
        net = ipaddr.IPv4Network(net)
    except ipaddr.AddressValueError:
        return []

    if net.prefixlen == 32:
        return [net.ip]
    else:
        # 默认排除.1的网关地址
        return [ip for ip in net.iterhosts() if not (ip.is_private or ip.is_loopback)][1:]


def allocate_ippool_for_customer(customer_id=0, flag=False):
    """
    为用户分配IP发送池
    :param customer_id: 用户id, 默认为0, 表示为所有用户分配IP发送池
    :param flag: 是否重新分配池子, 默认为False, 表示如果用户分配了, 不重新分配
    :return:
    """
    returnv = False
    if customer_id:
        customers = Customer.objects.filter(id=customer_id)
    else:
        customers = Customer.objects.all()
    for c in customers:
        if c.ip_pool and not flag:
            continue
        free_pools = IpPool.objects.filter(type='auto').annotate(num_ip=Count('clusterip')).filter(
            num_ip__gt=0).annotate(num_customer=Count('customer', distinct=True)).order_by('num_customer')
        if free_pools:
            c.ip_pool = free_pools[0]
            c.save()
            returnv = True
    return returnv



