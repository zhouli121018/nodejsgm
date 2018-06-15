# -*- coding: utf-8 -*-
#
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.template.response import HttpResponse, TemplateResponse
from django.db.models import Q
from app.template.models import SendTemplate

def get_next_templates(request):
    data = request.GET
    template_ids = data.get('template_ids', [])
    if template_ids:
        template_ids = map(int, template_ids.split(','))
    page = int(data.get('page', 1))
    lists = SendTemplate.objects.filter(
        Q(user=request.user) | Q(sub_share_template__user=request.user)).filter(
        isvalid=True, result__in=['green', 'yellow', 'red_pass']).exclude(
        id__in=template_ids).order_by('-id')
    per_page = 5
    orphans = 0

    paginator = Paginator(lists, per_page, orphans)
    try:
        lists = paginator.page(page)
    except PageNotAnInteger:
        lists = paginator.page(1)
    except EmptyPage:
        lists = paginator.page(paginator.num_pages)
    t = TemplateResponse(request, 'task/ajax_load_template.html', {
        'lists': lists,
    })
    t.render()
    return HttpResponse(t.content, content_type="text/html")


def check_temlates_exists_pc(request, template_id):
    """ 检测模板是否在母子账户中。
    """
    try:
        SendTemplate.objects.get(id=template_id, user=request.user)
        return True
    except:
        try:
            SendTemplate.objects.get(id=template_id, user=request.user.parent)
            return True
        except:
            return False