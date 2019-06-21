# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class MyUser(models.Model):
    name = models.ForeignKey(
        'auth.User',
        limit_choices_to={'is_staff': True},
        verbose_name=u'用户名'
    )
    role = models.ManyToManyField('Role', verbose_name=u'一个用户拥有若干角色', blank=True)

    def __str__(self):
        return self.name.username

class Role(models.Model):
    name = models.CharField(max_length=16, unique=True, verbose_name=u'角色名')
    purview = models.ManyToManyField('Permission', verbose_name=u'一个角色拥有若干权限', blank=True)

    def __str__(self):
        return self.name

class Menu(models.Model):
    title = models.CharField(max_length=64, verbose_name=u'一级菜单')
    icon = models.CharField(blank=True, max_length=16, help_text=u'应填写ICON 名称，例如icon-home，参考ZUI框架文档-控件-图标')

    def __unicode__(self):
        return self.title

class Permission(models.Model):
    description = models.CharField(max_length=64, verbose_name=u'权限描述')
    url = models.CharField(max_length=64, blank=True, verbose_name=u'含正则的URL')
    url_pattern_name = models.CharField(blank=True, max_length=32, help_text = u'应与urls.py 里定义的url pattern name 完全一致')
    icon = models.CharField(blank=True, max_length=32)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True, blank=True, help_text=u'menu 为null 表示非菜单')
    related_id = models.ForeignKey(
        to='Permission',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=u'非菜单关联的权限',
        help_text = u'对于部分非菜单权限，应为其展开关联的菜单权限',
        limit_choices_to={'menu__isnull': False}  
    )

    def __unicode__(self):
        return self.description
