# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from zabbixapi import ZabbixAPI
from forms import AddForm

zabbixAPI = ZabbixAPI()

def add(request):
    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            hostname = form.cleaned_data['hostname']
            asset = form.cleaned_data['ip']
            group_id = form.cleaned_data['group_id']
            template_id = form.cleaned_data['template_id']
            if asset.ip:
                ip =  asset.ip
            elif asset.other_ip:
                ip = asset.other_ip
            else:
                ip = '127.0.0.1'
            if asset.asset_type in [2, 3]:
                returns = zabbixAPI.addSnmpDevice(hostname, ip, group_id, template_id)
            else:
                returns = zabbixAPI.addHost(hostname, ip, group_id, template_id)
            messages.add_message(request, messages.SUCCESS, u'创建成功：{0}'.format(returns))
            return HttpResponseRedirect(reverse('ADD'))
    else:
        form = AddForm()       
    return render(request, 'zabbix/add.html', locals())

def delete(request):
    host_list = zabbixAPI.getHostID()
    if request.method == 'POST':
        host_id = request.POST.getlist('host_id')
        for hostid in host_id:
            returns = zabbixAPI.delHost(hostid)
            if 'error' in returns:
                messages.add_message(request, messages.ERROR, 'host: {0}, error: {1}'.format(hostid, returns['error']))
                return HttpResponseRedirect(reverse('delete'))
        messages.add_message(request, messages.SUCCESS, u'删除成功')
        return HttpResponseRedirect(reverse('delete'))
    return render(request, 'zabbix/del.html', locals())
