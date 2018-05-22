#coding=utf-8
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from apps.core.models import UrlRemark
from django.http import HttpResponse
import json
import re

@login_required
def home(request, template_name='home.html'):
    return HttpResponseRedirect(reverse('customer_list'))
    # return HttpResponse('home')
    # return render_to_response(template_name, {
    # }, context_instance=RequestContext(request))


@login_required
def ajax_get_remark_base(request):
    data = request.GET
    base_url = data.get('base_url', '')
    lists = []
    if base_url:
        if re.search(r'(\/\d+?\/)', base_url):
            base_url = re.sub(r'(\/\d+?\/)', '/modify/', base_url)
        base_url = 'web' + base_url.strip('')
        lists = UrlRemark.objects.filter(url=base_url).values('remark')
    res = lists and lists[0] or {'remark': u'暂无'}
    return HttpResponse(json.dumps(res, ensure_ascii=False), content_type="application/json")

@login_required
def ajax_save_remark_base(request):
    data = request.POST
    base_url = data.get('base_url', '')
    remark = data.get('remark', '')
    if base_url:
        if re.search(r'(\/\d+?\/)', base_url):
            base_url = re.sub(r'(\/\d+?\/)', '/modify/', base_url)
        base_url = 'web' + base_url.strip('')
        obj, bool = UrlRemark.objects.get_or_create(url=base_url)
        obj.remark = remark
        if bool:
            obj.create_uid = request.user
        obj.write_uid = request.user
        obj.save()
    return HttpResponse(json.dumps({'msg': u"成功修改备注"}), content_type="application/json")

