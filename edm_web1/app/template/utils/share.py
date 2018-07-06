# -*- coding: utf-8 -*-
from django.http import Http404

def get_share_template_object(model, customer, pk):
    """
    获取customer所有的model对象
    :param model:
    :param customer:
    :param pk:
    :return:
    """
    try:
        return model.objects.get(user=customer, pk=pk)
    except:
        try:
            return model.objects.get(user=customer.parent, pk=pk)
        except:
            raise Http404

def get_share_mosaico_obj(model, customer, template_id):
    try:
        return model.objects.get(user_id=customer.id, template_id=template_id)
    except:
        try:
            return model.objects.get(user_id=customer.parent.id, template_id=template_id)
        except:
            raise Http404