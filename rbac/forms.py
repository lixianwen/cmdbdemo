#!/usr/bin/env python
#coding: utf8

from cmdb.utils import AddClass
from models import Menu, Permission, Role
from django.forms import ModelForm, ValidationError, TextInput

class AddMenuForm(ModelForm):
    class Meta:
        model = Menu
        fields = ['title', 'icon']

    def __init__(self, *args, **kwargs):
        super(AddMenuForm, self).__init__(*args, **kwargs)
        instance = AddClass(self.fields)

class SecondGradeMenuForm(ModelForm):
    class Meta:
        model = Permission
        exclude = ['related_id']

    def __init__(self, *args, **kwargs):
        super(SecondGradeMenuForm, self).__init__(*args, **kwargs)
        instance = AddClass(self.fields)

class PermissionForm(ModelForm):
    class Meta:
        model = Permission
        fields = ['description', 'url', 'icon', 'url_pattern_name']

    def __init__(self, *args, **kwargs):
        super(PermissionForm, self).__init__(*args, **kwargs)
        instance = AddClass(self.fields)

class MultiPermissionForm(ModelForm):
    class Meta:
        model = Permission
        exclude = ['icon']

    def __init__(self, *args, **kwargs):
        super(MultiPermissionForm, self).__init__(*args, **kwargs)
        instance = AddClass(self.fields)

class RoleForm(ModelForm):
    class Meta:
        model = Role
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
        }
