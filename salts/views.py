# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
import shlex
from models import Upload
from salt_api import SaltAPI
from django.urls import reverse
from cmdb.utils import validIPV4
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from subprocess import Popen, PIPE
from django.http import HttpResponseRedirect
from asset.models import IDC, PhysicalServer, Asset
from django.contrib.auth.decorators import permission_required
from forms import InstallForm, FileUploadForm, CommandForm, PushForm

# Create your views here.

saltapi = SaltAPI()
asset_list = Asset.objects.all()

@permission_required('auth.change_user')
def collect(request):
    response = dict()
    if request.method == 'POST':
        ip = request.POST.get('ip')
        if not validIPV4(ip):
            messages.add_message(request, messages.ERROR, u'IP地址不合法或格式不正确')
            return HttpResponseRedirect(reverse('collect'))
        for i in ['ipv4', 'num_cpus', 'mem_total', 'oscodename']:
            cmd = 'salt --out=json {0} grains.item {1}'.format(ip, i)
            try:
                p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
                stdout, stderr = p.communicate()
                response.update(json.loads(stdout)[ip])
            except Exception as e:
                break
                messages.add_message(request, messages.ERROR, e)
                messages.add_message(request, messages.ERROR, stderr)
                return HttpResponseRedirect(reverse('collect'))
        cmd = '/usr/bin/lsblk -d'
        p = Popen(shlex.split(cmd), stdout=PIPE)
        stdout = p.communicate()[0]
        response.update({'disk': stdout})
        response = json.dumps(response)
        return HttpResponse(response)
    return render(request, 'salts/collect.html')

@permission_required('auth.change_user')
def command(request):
    if request.method == 'POST':
        form = CommandForm(request.POST)
        if form.is_valid():
            asset_instance = form.cleaned_data['minion']
            cmd = form.cleaned_data['cmd']
            if asset_instance.ip:
                response = saltapi.cmd(asset_instance.ip, cmd)
            elif asset_instance.other_ip:
                response = saltapi.cmd(asset_instance.other_ip, cmd)
            else:
                messages.add_message(request, messages.ERROR, u'不是虚拟机，不能执行salt任务')
                return HttpResponseRedirect(reverse('command'))
            return HttpResponse(response)
    form = CommandForm()
    return render(request, 'salts/command.html', locals())

@permission_required('auth.change_user')
def install(request):
    if request.method == 'POST':
        form = InstallForm(request.POST)
        if form.is_valid():
            ip = form.cleaned_data['ip']
            release = int(form.cleaned_data['release'])
            if release == 6:
                response = saltapi.minion(ip, 'saltminion.install_6')
                messages.add_message(request, messages.SUCCESS, u'安装中，请耐心等待')
            else:
                response = saltapi.minion(ip, 'saltminion.install_7')
                messages.add_message(request, messages.SUCCESS, u'安装中，请耐心等待')
    else:
        form = InstallForm()
    return render(request, 'salts/install.html', locals())

@permission_required('auth.change_user')
def upload(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = Upload()
            f.filename = form.cleaned_data['file']
            f.save()
#        messages.add_message(request, messages.SUCCESS, u'文件 {0} 上传成功, 大小为{1}KB'.format(f.filename.name.split('/')[-1], int(f.filename.size)/1024))
#        return HttpResponseRedirect(reverse('push'))
        return HttpResponse(u'文件 {0} 上传成功, 大小为{1}KB'.format(f.filename.name.split('/')[-1], int(f.filename.size)/1024))
#    form = FileUploadForm()
#    return render(request, 'salts/upload.html', locals())

def check_file():
    for f in Upload.objects.all():
        if f.filename.name.split('/')[-1] not in os.listdir(settings.MEDIA_ROOT + '/upload'):
            Upload.objects.get(pk=f.pk).delete()

@permission_required('auth.change_user')
def push(request):
    check_file()
    if request.method == 'POST':
        hosts = request.POST.getlist('host')
        push_file = request.POST.get('push_file')
        dest = request.POST.get('dest')
        result = list()
        for host in hosts:
            asset = Asset.objects.get(id=int(host))
            if asset.ip:
                jid1 = saltapi.pushFile(asset.ip, push_file, dest)
                result.append(jid1)
            elif asset.other_ip:
                jid2 = saltapi.pushFile(asset.other_ip, push_file, dest)
                result.append(jid2)
        result = json.dumps(result)
        return HttpResponse(result)
    file_list = Upload.objects.all()
    form = FileUploadForm()
    locals().update({'asset_list': asset_list})
    return render(request, 'salts/push.html', locals())

@permission_required('auth.change_user')
def job(request):
    if request.method == 'POST':
        jid = request.POST.get('jid')
        response = saltapi.getReuslt(jid)
        return HttpResponse(response)
    return render(request, 'salts/result.html')

@permission_required('auth.change_user')
def script(request):
    check_file()
    file_list = Upload.objects.all()
    upload_form = FileUploadForm()
    if request.method == 'POST':
        hosts = request.POST.getlist('host')
        f_script = request.POST.get('script')
        result = list()
        for host in hosts:
            asset = Asset.objects.get(id=int(host))
            if asset.ip:
                jid1 = saltapi.exeScript(asset.ip, f_script)
                result.append(jid1)
            elif asset.other_ip:
                jid2 = saltapi.exeScript(asset.other_ip, f_script)
                result.append(jid2)
        result = json.dumps(result)
        return HttpResponse(result)
    locals().update({'asset_list': asset_list})
    return render(request, 'salts/script.html', locals())
