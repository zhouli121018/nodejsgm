# coding=utf-8
from django.http import Http404
from app.core.models import Customer

def get_customer_child_obj(request, user_id):
    """
    获取customer所有的model对象
    :param request:
    :param user_id:
    :return:
    """
    obj = Customer.objects.filter(id=user_id, parent=request.user).first()
    if obj:
        return obj
    else:
        raise Http404