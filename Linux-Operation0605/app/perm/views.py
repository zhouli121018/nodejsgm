# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.contrib.auth.backends import ModelBackend
from app.core.models import User as MyUser
from .models import MyPermission
from .forms import MyPermissionForm, GroupForm, UserCreationForm, PasswordChangeForm, SetPasswordForm
from app.utils.decorators import superuser_required

@superuser_required
@login_required
def perm_list(request):
    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == 'delete':
            perm_id = request.POST.get('perm_id', '')
            if perm_id:
                MyPermission.objects.get(id=perm_id).delete()
                messages.add_message(request, messages.SUCCESS, u'删除成功')
        return HttpResponseRedirect(reverse('perm_list'))
    permlists = MyPermission.objects.filter(parent__isnull=True).order_by('order_id')
    return render(request, "perm/perm_list.html",
                  { 'permlists': permlists })

@superuser_required
@login_required
def perm_add(request):
    form = MyPermissionForm()
    if request.method == "POST":
        form = MyPermissionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加成功')
            return HttpResponseRedirect(reverse('perm_list'))
    return render(request, "perm/perm_modify.html",
                  { 'form': form })

@superuser_required
@login_required
def perm_modify(request, perm_id):
    perm_obj = MyPermission.objects.get(id=perm_id)
    form = MyPermissionForm(instance=perm_obj)
    if request.method == "POST":
        form = MyPermissionForm(request.POST, instance=perm_obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改成功')
            return HttpResponseRedirect(reverse('perm_list'))
    return render(request, "perm/perm_modify.html",
                  { 'form': form })

@superuser_required
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
    return render(request, "perm/group_list.html",
                  {'groups': groups })

@superuser_required
@login_required
def group_add(request):
    form = GroupForm()
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('group_list'))
    return render(request, "perm/group_modify.html",
                  { 'form': form })

@superuser_required
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
    return render(request, "perm/group_modify.html",
                  {'form': form})

@superuser_required
@login_required
def perm_grant(request):
    g_id = request.GET.get('g_id', '')
    u_id = request.GET.get('u_id', '')
    mypermissions = MyPermission.objects.filter(parent__isnull=True).order_by('order_id')
    if g_id:
        obj = Group.objects.get(id=g_id)
        perms = obj.permissions.values_list('content_type__app_label', 'codename').order_by()
        perms = set("%s.%s" % (ct, name) for ct, name in perms)
    if u_id:
        obj = MyUser.objects.get(id=u_id)
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
        # return HttpResponseRedirect(reverse('user_list'))
        return HttpResponseRedirect(request.get_full_path())
    return render(request, "perm/perm_grant.html", {
        'mypermissions': mypermissions,
        'myperms': perms,
        'obj': obj,
    })

@superuser_required
@login_required
def user_list(request):
    data = request.GET
    users = get_user_data(data)
    if request.method == "POST":
        action = request.POST.get('action', '')
        user_id = request.POST.get('id', '')
        if user_id:
            obj = MyUser.objects.get(id=user_id)
            if action == 'delete':
                if obj.is_superuser:
                    messages.add_message(request, messages.ERROR, u'超级用户不能被删除')
                else:
                    obj.delete()
                    messages.add_message(request, messages.SUCCESS, u'删除成功')
            if action == 'disabled':
                if obj.is_superuser:
                    messages.add_message(request, messages.ERROR, u'超级用户不能被禁用')
                else:
                    obj.is_active=False
                    obj.save()
                    messages.add_message(request, messages.SUCCESS, u'禁用成功')
            if action == 'active':
                obj.is_active = True
                obj.save()
                messages.add_message(request, messages.SUCCESS, u'激活成功')
            if action == 'super':
                obj.is_superuser = True
                obj.save()
                messages.add_message(request, messages.SUCCESS, u'设为超级用户成功')
            if action == 'unsuper':
                if request.user == obj:
                    raise Http404
                count = MyUser.objects.filter(is_superuser=True).count()
                if count<=1:
                    messages.add_message(request, messages.ERROR, u'取消超级用户失败，平台至少保留一个超级用户')
                else:
                    obj.is_superuser = False
                    obj.save()
                    messages.add_message(request, messages.SUCCESS, u'取消超级用户成功')
        return HttpResponseRedirect(reverse('user_list'))
    return render(request, "perm/user_list.html", {
        'users': users,
    })

def get_user_data(data):
    username = data.get('username', '')
    user_id = data.get('user_id', '')
    group_id = data.get('group_id', '')
    if group_id:
        group = Group.objects.get(id=group_id)
        users = group.user_set.all()
    else:
        users = MyUser.objects.all()
    if username:
        users = users.filter(username__icontains=username)
    if user_id:
        users = users.filter(id=user_id)
    return users

@superuser_required
@login_required
def user_add(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'用户添加成功')
            return HttpResponseRedirect(reverse('user_list'))
    return render(request, "perm/user_add.html",
                  { 'form': form })

@superuser_required
@login_required
def user_modify(request, user_id):
    user_obj = MyUser.objects.get(id=user_id)
    user_group_ids = user_obj.groups.values_list('id', flat=True)
    groups = Group.objects.all()
    if request.method == "POST":
        group_ids = request.POST.getlist('name[]', [])
        group_ids = map(int, group_ids)
        perms = Group.objects.filter(id__in=group_ids)
        user_obj.groups.clear()
        user_obj.groups = perms
        messages.add_message(request, messages.SUCCESS, u'信息修改成功')
        return HttpResponseRedirect(reverse('user_list'))
    return render(request, "perm/user_modify.html", {
        'user_obj': user_obj,
        'user_id': user_id,
        'user_group_ids': user_group_ids,
        'groups': groups,
    })

@superuser_required
@login_required
def user_passwd_change(request, user_id):
    user_obj = MyUser.objects.get(id=user_id)
    form = PasswordChangeForm(user_obj)
    if request.method == "POST":
        form = PasswordChangeForm(user_obj, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'密码修改成功')
            return HttpResponseRedirect(reverse('user_list'))
    return render(request, "perm/user_passwd_change.html",
                  { 'form': form, 'user_obj': user_obj })

@superuser_required
@login_required
def user_passwd_set(request, user_id):
    user_obj = MyUser.objects.get(id=user_id)
    form = SetPasswordForm(user_obj)
    if request.method == "POST":
        form = SetPasswordForm(user_obj, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'密码修改成功')
            return HttpResponseRedirect(reverse('user_list'))
    return render(request, "perm/user_passwd_change.html",
                  { 'form': form, 'user_obj': user_obj })
