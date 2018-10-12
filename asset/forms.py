#!/usr/bin/env python
#coding:utf8

from django import forms
from cmdb.utils import validIPV4
from models import IDC, PhysicalServer, Asset
from django.forms import ModelForm, Textarea, Select
from django.utils.translation import ugettext_lazy as _

class IdcForm(ModelForm):
    class Meta:
        model = IDC
        fields = ['name', 'address', 'linkman', 'ci', 'bandwidth', 'ip_segment', 'comment']
        widgets = {'ip_segment': Textarea}

class PhysicalServerForm(ModelForm):
    class Meta:
        model = PhysicalServer
        fields = ['manufacturer', 'model', 'sn', 'ip', 'cpu', 'memory', 'disk', 'nic_num', 'comment']
        error_messages = {
            'ip': {
                'invalid': _(u'IP地址不合法'),
            },
        }

class AssetForm(ModelForm):
    class Meta:
        model = Asset
        fields = ['ip', 'other_ip', 'idc', 'hostname', 'cpu', 'memory', 'disk', 'system', 'status', 'asset_type', 'env', 'host', 'comment']
        widgets = {
            'status': Select(attrs={'required': True}),
            'asset_type': Select(attrs={'required': True}),
            'env': Select(attrs={'required': True})
        }

    def customValidIP(self, ip):
        if ip:
            if not validIPV4(ip):
                raise forms.ValidationError(u'IP地址不合法')
        return ip

    def clean_ip(self):
        return self.customValidIP(self.cleaned_data['ip'])

    def clean_other_ip(self):
        return self.customValidIP(self.cleaned_data['other_ip'])
