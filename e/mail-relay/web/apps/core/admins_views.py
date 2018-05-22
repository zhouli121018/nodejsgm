# coding=utf-8
import re
import json

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group, User
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.template.context import RequestContext
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.response import TemplateResponse
from django.db.models import Q

from apps.core.models import MyPermission
from forms import MyPermissionForm, GroupForm, UserForm, SuperUserForm


@login_required
def mypermission_list(request):
    mypermissions = MyPermission.objects.filter(parent__isnull=True).order_by('order')

    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == 'delete':
            mypermission_id = request.POST.get('id', '')
            if mypermission_id:
                MyPermission.objects.get(id=mypermission_id).delete()
                messages.add_message(request, messages.SUCCESS, u'删除成功')
        return HttpResponseRedirect(reverse('mypermission_list'))
    return render_to_response("core/mypermission_list.html", {
        'mypermissions': mypermissions,
    }, context_instance=RequestContext(request))


@login_required
def mypermission_add(request):
    form = MyPermissionForm()
    if request.method == "POST":
        form = MyPermissionForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('mypermission_list'))
    return render_to_response("core/mypermission_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def mypermission_modify(request, mypermission_id):
    mypermission_obj = MyPermission.objects.get(id=mypermission_id)
    form = MyPermissionForm(instance=mypermission_obj)
    if request.method == "POST":
        form = MyPermissionForm(request.POST, instance=mypermission_obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('mypermission_list'))
    return render_to_response("core/mypermission_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def group_list(request):
    groups = Group.objects.all()

    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == 'delete':
            group_id = request.POST.get('id', '')
            if group_id:
                Group.objects.get(id=group_id).delete()
                messages.add_message(request, messages.SUCCESS, u'删除成功')
        return HttpResponseRedirect(reverse('group_list'))
    return render_to_response("core/group_list.html", {
        'groups': groups,
    }, context_instance=RequestContext(request))


@login_required
def group_add(request):
    form = GroupForm()
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

            # 为新用户分配发送池
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('group_list'))
    return render_to_response("core/group_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def group_modify(request, group_id):
    group_obj = Group.objects.get(id=group_id)
    form = GroupForm(instance=group_obj)
    if request.method == "POST":
        form = GroupForm(request.POST, instance=group_obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('group_list'))
    return render_to_response("core/group_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def grant_permission(request):
    g_id = request.GET.get('g_id', '')
    u_id = request.GET.get('u_id', '')
    mypermissions = MyPermission.objects.filter(parent__isnull=True).order_by('order')
    if g_id:
        obj = Group.objects.get(id=g_id)
        perms = obj.permissions.values_list('content_type__app_label', 'codename').order_by()
        perms = set("%s.%s" % (ct, name) for ct, name in perms)
    if u_id:
        obj = User.objects.get(id=u_id)
        perms = ModelBackend().get_all_permissions(obj)

    if request.method == "POST":
        ids = request.POST.get('ids', '').split(',')
        ids = filter(lambda s: s.isdigit(), ids)
        permissions = []
        for p in MyPermission.objects.filter(id__in=ids):
            permissions.append(p.permission)
        if g_id:
            obj.permissions.clear()
            obj.permissions = permissions
        else:
            obj.user_permissions.clear()
            obj.user_permissions = permissions

        messages.add_message(request, messages.SUCCESS, u'信息修改成功')
        return HttpResponseRedirect(request.get_full_path())
    return render_to_response("core/grant_permission.html", {
        'mypermissions': mypermissions,
        'myperms': perms,
        'obj': obj,
    }, context_instance=RequestContext(request))


@login_required
def user_list(request):
    users = User.objects.all()

    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == 'delete':
            user_id = request.POST.get('id', '')
            if user_id:
                User.objects.get(id=user_id).delete()
                messages.add_message(request, messages.SUCCESS, u'删除成功')
        return HttpResponseRedirect(reverse('user_list'))
    return render_to_response("core/user_list.html", {
        'users': users,
    }, context_instance=RequestContext(request))


@login_required
def user_add(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True
            user.save()

            # 为新用户分配发送池
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('user_list'))
    return render_to_response("core/user_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def user_modify(request, user_id):
    user_obj = User.objects.get(id=user_id)
    userform = SuperUserForm if request.user.is_superuser else UserForm
    form = userform(instance=user_obj)
    if request.method == "POST":
        form = userform(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('user_list'))
    return render_to_response("core/user_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def password_modify(request, user_id):
    user_obj = User.objects.get(id=user_id)
    form = SetPasswordForm(user=user_obj)
    if request.method == "POST":
        form = SetPasswordForm(user_obj, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('user_list'))
    return render_to_response("core/password_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


def get_user_data(data):
    username = data.get('username', '')
    email = data.get('email', '')
    user_id = data.get('user_id', '')
    group_id = data.get('group_id', '')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'username', 'email', 'first_name', 'last_name', 'id', 'id', 'is_active', 'is_superuser',
              'date_joined', 'last_login', 'id']
    if group_id:
        group = Group.objects.get(id=group_id)
        users = group.user_set.all()
    else:
        users = User.objects.all()
    if username:
        users = users.filter(username__icontains=username)
    if user_id:
        users = users.filter(id=user_id)
    if email:
        users = users.filter(email__icontains=email)
    if first_name:
        users = users.filter(first_name__icontains=first_name)
    if last_name:
        users = users.filter(last_name__icontains=last_name)

    if search:
        users = users.filter(
            Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(
                email__icontains=search))

    if users and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            users = users.order_by('-%s' % colums[int(order_column)])
        else:
            users = users.order_by('%s' % colums[int(order_column)])
    return users


@login_required
def ajax_get_users(request):
    data = request.GET

    users = get_user_data(data)

    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    count = len(users)

    paginator = Paginator(users, length)

    try:
        users = paginator.page(page)
    except (EmptyPage, InvalidPage):
        users = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    for c in users.object_list:
        t = TemplateResponse(request, 'core/ajax_get_user.html', {'g': c})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

