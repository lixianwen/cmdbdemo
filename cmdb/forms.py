#!/usr/bin/env python
#coding: utf8

from django import forms
from cmdb.utils import AddClass

class LoginForm(forms.Form):
    username = forms.CharField(max_length=16, label=u'用户名')
    password = forms.CharField(widget=forms.PasswordInput, label=u'密码')
    verification_code = forms.CharField(max_length=4, label=u'验证码')
    remember = forms.BooleanField(required=False, label=u'记住密码')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        instance = AddClass(self.fields)
