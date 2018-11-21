#!/usr/bin/env python
#coding:utf8

from django import forms
from asset.models import Asset
from zabbixapi import ZabbixAPI

zabbixApi = ZabbixAPI()

def getGroupid():
    response = zabbixApi.getHostGroupID()
    groupid_list = list()
    for i in response:
        groupid_list.append((int(i['groupid']), i['name']))
    return groupid_list

def getTemplateid():
    response = zabbixApi.getTemplateID()
    template_list = list()
    for i in response:
        template_list.append((int(i['templateid']), i['name']))
    return template_list

def getHostid():
    response = zabbixApi.getHostID()
    host_list = list()
    for i in response:
        host_list.append((int(i['hostid']), i['host']))
    return host_list

class AddForm(forms.Form):
    hostname = forms.CharField(label=u'主机名称')
    ip = forms.ModelChoiceField(queryset=Asset.objects.all(), label=u'IP地址', empty_label=None)
    group_id = forms.ChoiceField(choices=getGroupid(), label=u'主机群组')
    template_id = forms.MultipleChoiceField(
                                choices=getTemplateid(),
                                widget=forms.SelectMultiple(attrs={'size': 6}),
                                label=u'模版') 

    def clean_ip(self):
        asset_instance = self.cleaned_data['ip']
        if asset_instance.asset_type == 4:
            raise forms.ValidationError(u'不支持添加该设备，请到控制台手动添加')
        return asset_instance

    def clean_hostname(self):
        hostname = self.cleaned_data['hostname']
        if zabbixApi.hostExists(hostname):
            raise forms.ValidationError('host {0} has already exists'.format(hostname))
        return hostname
