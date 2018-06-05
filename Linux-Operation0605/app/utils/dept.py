# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app.core.models import Department

def display(depts):
    """
    [[1, [2, [3, 3]],[1, [2, [3, 3]]]
    :param depts:
    :return:
    """
    lists = []
    for d in depts:
        lists.append(d)

        children = Department.objects.filter(parent_id=d.id)
        if len(children) > 0:
            lists.append(display(children))
    return lists


def display2(depts, level=0):
    """
    [[a, 1], [b, 2], [c, 3], [d, 3], [a, 1]]
    :param depts:
    :return:
    """
    lists = []
    for d in depts:
        lists.append([d, level])
        children = Department.objects.filter(parent_id=d.id)
        if children:
            lists.extend(display2(children, level + 1))
    return lists

