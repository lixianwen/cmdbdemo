#!/usr/bin/env python
#coding:utf8

from django import forms
from asset.models import Asset
from models import Upload
from cmdb.utils import validIPV4

SYSTEM = (
    (6, 'Centos 6'),
    (7, 'Centos 7'),
)

class InstallForm(forms.Form):
    ip = forms.GenericIPAddressField(protocol='IPv4', error_messages={'invalid': u'IP地址不合法'})
    release = forms.ChoiceField(choices=SYSTEM, widget=forms.RadioSelect, label=u'系统版本')

class FileUploadForm(forms.Form):
    file = forms.FileField()

class CommandForm(forms.Form):
    minion = forms.ModelChoiceField(queryset=Asset.objects.all())
    cmd = forms.CharField(label=u'命令', help_text=u'只支持单个命令')

class PushForm(forms.Form):
    minion = forms.ModelMultipleChoiceField(queryset=Asset.objects.all(), help_text=u'选择主机，支持单台主机或多台主机（按ctrl多选）')
    file = forms.ModelChoiceField(queryset=Upload.objects.all(), label=u'选择文件')
    dest_dir = forms.CharField(label=u'目标目录', widget=forms.TextInput(attrs={'placeholder': u'请填写绝对路径'}))
