# -*- coding: utf-8 -*-

from django.shortcuts import render

from django.contrib.auth.decorators import login_required


from lib import tools

@login_required
def support(request):
    return render(request, template_name='support/support.html', context={
    })
