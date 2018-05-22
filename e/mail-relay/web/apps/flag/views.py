# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from apps.flag.models import NotExistFlag, BigQuotaFlag, SpamFlag, NotRetryFlag, SpfFlag, HighRiskFlag, GreyListFlag
from apps.flag.forms import NotExistFlagForm, BigQuotaFlagForm, SpamFlagForm, NotRetryFlagForm, SpfFlagForm, HighRiskFlagForm, GreyListFlagForm

@login_required
def not_exist_flag_list(request):
    not_exist_flags = NotExistFlag.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = NotExistFlag.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            NotExistFlag.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("flag/not_exist_flag_list.html", {
        'not_exist_flags': not_exist_flags,
    }, context_instance=RequestContext(request))

@login_required
def not_exist_flag_add(request):
    form = NotExistFlagForm()
    if request.method == "POST":
        form = NotExistFlagForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('not_exist_flag_list'))
    return render_to_response("flag/not_exist_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def not_exist_flag_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = NotExistFlagForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('not_exist_flag_list'))
    return render_to_response("flag/not_exist_flag_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def not_exist_flag_modify(request, not_exist_flag_id):
    not_exist_flag_obj = NotExistFlag.objects.get(id=not_exist_flag_id)
    form = NotExistFlagForm(instance=not_exist_flag_obj)
    if request.method == "POST":
        form = NotExistFlagForm(request.POST, instance=not_exist_flag_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('not_exist_flag_list'))
    return render_to_response("flag/not_exist_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def big_quota_flag_list(request):
    big_quota_flags = BigQuotaFlag.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = BigQuotaFlag.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            BigQuotaFlag.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("flag/big_quota_flag_list.html", {
        'big_quota_flags': big_quota_flags,
    }, context_instance=RequestContext(request))


@login_required
def big_quota_flag_add(request):
    form = BigQuotaFlagForm()
    if request.method == "POST":
        form = BigQuotaFlagForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('big_quota_flag_list'))
    return render_to_response("flag/big_quota_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def big_quota_flag_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = BigQuotaFlagForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('big_quota_flag_list'))
    return render_to_response("flag/big_quota_flag_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def big_quota_flag_modify(request, big_quota_flag_id):
    big_quota_flag_obj = BigQuotaFlag.objects.get(id=big_quota_flag_id)
    form = BigQuotaFlagForm(instance=big_quota_flag_obj)
    if request.method == "POST":
        form = BigQuotaFlagForm(request.POST, instance=big_quota_flag_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('big_quota_flag_list'))
    return render_to_response("flag/big_quota_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def spam_flag_list(request):
    spam_flags = SpamFlag.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = SpamFlag.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            SpamFlag.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("flag/spam_flag_list.html", {
        'spam_flags': spam_flags,
    }, context_instance=RequestContext(request))


@login_required
def spam_flag_add(request):
    form = SpamFlagForm()
    if request.method == "POST":
        form = SpamFlagForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('spam_flag_list'))
    return render_to_response("flag/spam_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def spam_flag_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = SpamFlagForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('spam_flag_list'))
    return render_to_response("flag/spam_flag_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def spam_flag_modify(request, spam_flag_id):
    spam_flag_obj = SpamFlag.objects.get(id=spam_flag_id)
    form = SpamFlagForm(instance=spam_flag_obj)
    if request.method == "POST":
        form = SpamFlagForm(request.POST, instance=spam_flag_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('spam_flag_list'))
    return render_to_response("flag/spam_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def not_retry_flag_list(request):
    not_retry_flags = NotRetryFlag.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = NotRetryFlag.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            NotRetryFlag.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("flag/not_retry_flag_list.html", {
        'not_retry_flags': not_retry_flags,
    }, context_instance=RequestContext(request))

@login_required
def not_retry_flag_add(request):
    form = NotRetryFlagForm()
    if request.method == "POST":
        form = NotRetryFlagForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('not_retry_flag_list'))
    return render_to_response("flag/not_retry_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def not_retry_flag_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = NotRetryFlagForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('not_retry_flag_list'))
    return render_to_response("flag/not_retry_flag_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def not_retry_flag_modify(request, not_retry_flag_id):
    not_retry_flag_obj = NotRetryFlag.objects.get(id=not_retry_flag_id)
    form = NotRetryFlagForm(instance=not_retry_flag_obj)
    if request.method == "POST":
        form = NotRetryFlagForm(request.POST, instance=not_retry_flag_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('not_retry_flag_list'))
    return render_to_response("flag/not_retry_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def spf_flag_list(request):
    spf_flags = SpfFlag.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = SpfFlag.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            SpfFlag.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("flag/spf_flag_list.html", {
        'spf_flags': spf_flags,
    }, context_instance=RequestContext(request))

@login_required
def spf_flag_add(request):
    form = SpfFlagForm()
    if request.method == "POST":
        form = SpfFlagForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('spf_flag_list'))
    return render_to_response("flag/spf_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def spf_flag_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = SpfFlagForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('spf_flag_list'))
    return render_to_response("flag/spf_flag_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def spf_flag_modify(request, spf_flag_id):
    spf_flag_obj = SpfFlag.objects.get(id=spf_flag_id)
    form = SpfFlagForm(instance=spf_flag_obj)
    if request.method == "POST":
        form = SpfFlagForm(request.POST, instance=spf_flag_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('spf_flag_list'))
    return render_to_response("flag/spf_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def high_risk_flag_list(request):
    high_risk_flags = HighRiskFlag.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = HighRiskFlag.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            HighRiskFlag.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("flag/high_risk_flag_list.html", {
        'high_risk_flags': high_risk_flags,
    }, context_instance=RequestContext(request))

@login_required
def high_risk_flag_add(request):
    form = HighRiskFlagForm()
    if request.method == "POST":
        form = HighRiskFlagForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('high_risk_flag_list'))
    return render_to_response("flag/high_risk_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def high_risk_flag_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = HighRiskFlagForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('high_risk_flag_list'))
    return render_to_response("flag/high_risk_flag_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def high_risk_flag_modify(request, high_risk_flag_id):
    high_risk_flag_obj = HighRiskFlag.objects.get(id=high_risk_flag_id)
    form = HighRiskFlagForm(instance=high_risk_flag_obj)
    if request.method == "POST":
        form = HighRiskFlagForm(request.POST, instance=high_risk_flag_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('high_risk_flag_list'))
    return render_to_response("flag/high_risk_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))



@login_required
def greylist_flag_list(request):
    greylist_flags = GreyListFlag.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = GreyListFlag.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            GreyListFlag.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("flag/greylist_flag_list.html", {
        'greylist_flags': greylist_flags,
    }, context_instance=RequestContext(request))

@login_required
def greylist_flag_add(request):
    form = GreyListFlagForm()
    if request.method == "POST":
        form = GreyListFlagForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('greylist_flag_list'))
    return render_to_response("flag/greylist_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def greylist_flag_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = GreyListFlagForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('greylist_flag_list'))
    return render_to_response("flag/greylist_flag_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def greylist_flag_modify(request, greylist_flag_id):
    greylist_flag_obj = GreyListFlag.objects.get(id=greylist_flag_id)
    form = GreyListFlagForm(instance=greylist_flag_obj)
    if request.method == "POST":
        form = GreyListFlagForm(request.POST, instance=greylist_flag_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('greylist_flag_list'))
    return render_to_response("flag/greylist_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))
