#!/usr/bin/env python
#coding: utf8

from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=16, label=u'用户名')
    password = forms.CharField(widget=forms.PasswordInput, label=u'密码')
    remember = forms.BooleanField(required=False, label=u'记住密码', help_text=u'这里仅表示如何实现浏览器保存登录信息，与session框架无关')
