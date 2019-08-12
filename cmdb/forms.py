#!/usr/bin/env python
#coding: utf8

from django import forms
from cmdb.utils import AddClass
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    """
    Subclass AuthenticationForm and add tow extra fields.
    If you want someone who has been authenticated access the login page will be redirected,
    just set redirect_authenticated_user attribute to True
    """
    verification_code = forms.CharField(max_length=4, label=u'验证码')
    remember = forms.BooleanField(required=False, label=u'记住密码')

    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        instance = AddClass(self.fields)

    def clean_verification_code(self):
        query_code = self.request.session.get('verify_code')
        posted_code = self.cleaned_data.get('verification_code')
        if query_code != posted_code:
            raise forms.ValidationError('Verification code error.')
        return posted_code
