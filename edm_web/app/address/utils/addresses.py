# coding=utf-8
from django.http import Http404
from app.address.models import MailList

def get_address_obj(request, list_id):
    """ 获取地址池对象。
    """
    try:
        return MailList.objects.get(id=list_id, customer=request.user)
    except:
        try:
            return MailList.objects.get(id=list_id, customer=request.user.parent)
        except:
            raise Http404

def get_address_userid(request, list_id):
    """ 获取用户id。
    """
    try:
        return MailList.objects.get(id=list_id, customer=request.user).customer_id
    except:
        try:
            return MailList.objects.get(id=list_id, customer=request.user.parent).customer_id
        except:
            return 0


def check_address_exists_pc(request, list_id):
    """ 检测地址池是否在母子账户中。
    """
    try:
        MailList.objects.get(id=list_id, customer=request.user)
        return True
    except:
        try:
            MailList.objects.get(id=list_id, user=request.user.parent)
            return True
        except:
            return False


def get_subject(request, list_id, obj=None):
    try:
        if obj:
            return obj.subject
        return MailList.objects.get(id=list_id, customer=request.user).subject
    except:
        return MailList.objects.get(id=list_id, customer=request.user.parent).subject
