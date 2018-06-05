# -*- coding: utf-8 -*-
from app.core.models import Domain

def get_domainid_bysession(request):
    """ 获取操作域名ID
    :param request:
    :return:
    """
    try:
        domain_id = int(request.session.get('domain_id', None))
    except:
        domain_id = 0
    if not domain_id:
        obj = Domain.objects.order_by('id').first()
        if obj:
            domain_id = obj.id
            request.session['domain_id'] = domain_id
    return domain_id

def get_session_domain(domain_id):
    obj = Domain.objects.filter(id=domain_id).first()
    return obj and obj.domain or None