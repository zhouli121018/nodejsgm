# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from app.core.models import Department, Mailbox, MailboxUser, DepartmentMember


@login_required
def choose_department_list(request):
    lists = Department.objects.all()
    department_id = request.GET.get('model_department_id', '0')
    department_id = department_id and int(department_id) or 0
    obj = Department.objects.filter(pk=department_id).first()
    department_name = obj and obj.title or ""
    return render(request, template_name='core/choose_department_list.html', context={
        'lists': lists,
        'department_id': department_id,
        'department_name': department_name,
    })

@login_required
def choose_mailbox_list(request):
    """
    {% url 'choose_mailbox_list' %}
    mbox/ch/?domain_id=x&action=y
    action:
        all             :   全家桶
        dept_list       :    部门列表
        dept_member    :    部门成员
            &dept_id=z
    返回值
    {
        mailbox:[
            {"id" : x, "box":k, name" : y, "dept_id" : z,}
        ]
        dept:[
            {"id":x, "name":y, "parent":z, "child":"1", "member": xx } 若无子部门则 child 不存在 member代表帐号数量
        ]
    }
    """
    def get_dept_list( lists_dpt ):
        dataDept = {}
        for obj in lists_dpt:
            dataDept[obj.id] = {
                            "id"        :   obj.id,
                            "name"      :   obj.title,
                            "parent"    :   obj.parent_id,
                        }
        for sub_id in dataDept.keys():
            sub = dataDept[sub_id]

            dataDept[sub_id]["member"] = len(DepartmentMember.objects.filter(dept_id=sub_id))
            parent_id = int(sub["parent"])
            if parent_id in (0,-1):
                continue
            if parent_id in dataDept:
                dataDept[parent_id]["child"] = 1
        return dataDept.values()
    #end get_dept_list

    action = request.GET.get('action', 'all')

    domain_id = request.GET.get('domain_id', '')
    domain_id = 0 if not domain_id else int(domain_id)

    if not domain_id:
        lists_dpt = Department.objects.all()
        lists_mbox = Mailbox.objects.all()
    else:
        lists_dpt = Department.objects.filter(domain_id=domain_id).all()
        lists_mbox = Mailbox.objects.filter(domain_id=domain_id).all()

    data = { "mailbox" : [], "dept" : [] }
    if action == "all":
        for obj in lists_mbox:
            objUser = MailboxUser.objects.filter(id=obj.id).first()
            name = u"未知用户" if not objUser else objUser.realname
            objMember = DepartmentMember.objects.filter(mailbox_id=obj.id).first()
            dept_id = -1 if not objMember else objMember.dept_id
            data["mailbox"].append( {
                    "id"        :   obj.id,
                    "box"       :   obj.mailbox,
                    "name"      :   name,
                    "dept_id"   :   dept_id,
                }
            )
        data["dept"] = get_dept_list( lists_dpt )
    elif action == "dept_list" :
        data["dept"] = get_dept_list( lists_dpt )
    elif action == "dept_member" :
        dept_id = request.GET.get('dept_id', '')
        dept_id = -1 if not dept_id else int(dept_id)
        lists_member = DepartmentMember.objects.filter(dept_id=dept_id).all()
        for objMember in lists_member:
            objBox = lists_mbox.filter(id=objMember.mailbox_id).first()
            if not objBox:
                continue
            objUser = MailboxUser.objects.filter(id=objBox.id).first()
            name = u"未知用户" if not objUser else objUser.realname
            data["mailbox"].append( {
                                "id"        :   objBox.id,
                                "box"       :   objBox.mailbox,
                                "name"      :   name,
                                "dept_id"   :   dept_id,
                            }
                        )
    return HttpResponse(json.dumps(data), content_type="application/json")
