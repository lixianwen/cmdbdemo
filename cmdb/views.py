#!/usr/bin/env python
#coding:utf8

import os
import mimetypes
from forms import LoginForm
from verifycode import VeifyCode
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from django.db.models import Count
from django.contrib import auth, messages
from django.contrib.auth.models import User
from asset.models import PhysicalServer, IDC, Asset
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse, HttpResponseRedirect

@login_required(login_url='/login/')
def index(request):
    idc_number = IDC.objects.aggregate(idc_number=Count('name'))['idc_number']
    ps_number = PhysicalServer.objects.aggregate(ps_number=Count('sn'))['ps_number']
    host_number = Asset.objects.aggregate(host_number=Count('asset_type'))['host_number']
    online_user = request.user.username
    return render(request, 'index.html', locals())

def loginview(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            code = form.cleaned_data['verification_code']
            text = request.session.get('verify_code', '')
            if text != code:
                error = '验证码错误，请重新登录'
                messages.add_message(request, messages.ERROR, error)
                return HttpResponseRedirect(reverse('loginview'))
            user = auth.authenticate(username=username, password=password)
            if not user:
                error = 'Invalid user or incorrect password.'
                messages.add_message(request, messages.ERROR, error)
                return HttpResponseRedirect(reverse('loginview'))
            elif not user.is_staff:
                error = 'user {0} is not allow logged in.'.format(username)
                messages.add_message(request, messages.ERROR, error)
                return HttpResponseRedirect(reverse('loginview'))
            else:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
    form = LoginForm()
    return render(request, 'registration/login.html', locals())

def logoutview(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))

def image(request):
    verifyCode = VeifyCode()
    content, buf_str = verifyCode.getImage()
    request.session.pop('verify_code', '')
    request.session['verify_code'] = content
    return HttpResponse(buf_str, content_type='mage/png')

def verify(request):
    if request.method == 'POST':
        verify_code = request.session.get('verify_code', '')
        code = request.POST.get('verification_code', '')
        if verify_code != code.lower():
            return HttpResponse('false')
        else:
            return HttpResponse('true')

def verify_password(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if not user:
            return HttpResponse('false')
        else:
            return HttpResponse('true')

def tpl_download(request, filename, extension):
    tpl_path = os.path.join(settings.BASE_DIR, 'tpl', filename)
    content_type = mimetypes.guess_type(tpl_path)[0]
    response = FileResponse(open(tpl_path, 'rb'), content_type=content_type)
    response['Content-Disposition'] = 'attachment;filename={0}'.format(filename)
    return response
