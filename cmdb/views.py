#!/usr/bin/env python
#coding:utf8

import os
import mimetypes
from forms import LoginForm
from verifycode import VeifyCode
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from django.db.models import Count
from forms import CustomAuthenticationForm
from django.contrib.auth.views import LoginView
from rbac.models import MyUser, Role, Permission
from asset.models import PhysicalServer, IDC, Asset
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse, HttpResponseRedirect

@login_required(login_url='/login/')
def index(request):
    idc_number = IDC.objects.aggregate(idc_number=Count('name'))['idc_number']
    ps_number = PhysicalServer.objects.aggregate(ps_number=Count('sn'))['ps_number']
    host_number = Asset.objects.aggregate(host_number=Count('asset_type'))['host_number']
    online_user = request.user.username
    return render(request, 'index.html', locals())

def initPermission(request, user_obj):
    '''
    获取登录用户的所有权限，并放入session
    数据结构：menu_mapping = [
                  {
                   'nodes': [
                       {
                        'url': u'/', 
                        'icon': u'icon-home', 
                        'id': 9, 
                        'title': u'首页'
                       }
                   ], 
                   'icon': u'icon-home', 
                   'title': u'首页'
                  }, 
                  {
                   'nodes': [
                       {
                        'url': u'/asset/list/', 
                        'icon': u'icon-info-sign', 
                        'id': 1, 
                        'title': u'服务器列表'
                       }, 
                       {
                        'url': u'/asset/add/', 
                        'icon': u'icon-edit-sign', 
                        'id': 2, 'title': u'添加服务器'
                       }
                   ], 
                   'icon': u'icon-server', 
                   'title': u'资产管理'
                  } 
              ]
              permission_mapping = {
                  '服务器列表': {
                      'url': u'/asset/list/', 
                      'related_id': None, 
                      'related_url': None, 
                      'related_description': None
                  },
                  '编辑服务器': {
                      'url': u'/asset/edit/(?P<pk>\\d+)/', 
                      'related_id': 1, 
                      'related_url': u'/asset/list/', 
                      'related_description': '服务器列表'
                  }
              }
    菜单顺序：父节点数据插入菜单表的顺序
    '''
    myuser = MyUser.objects.get(name__username=user_obj)
    permission_mapping = dict()
    menu_mapping = dict()
    permission_queryset = myuser.role.values(
        'purview__id',
        'purview__url',
        'purview__description',
        'purview__icon',
        'purview__menu_id',
        'purview__menu__title',
        'purview__menu__icon',
        'purview__related_id_id',
        'purview__related_id__url',
        'purview__related_id__description'
    )
    for item in permission_queryset:
        permission_mapping[item['purview__description']] = {
            'url': item['purview__url'],
            'related_id': item['purview__related_id_id'],
            'related_url': item['purview__related_id__url'],
            'related_description': item['purview__related_id__description']
        }
        menu_id = item['purview__menu_id']
        if menu_id is not None:
            node = {
                'id': item['purview__id'],
                'title': item['purview__description'],
                'url': item['purview__url'],
                'icon': item['purview__icon']
            }
            if menu_id in menu_mapping:
                menu_mapping[menu_id]['nodes'].append(node)
            else:
                title = item['purview__menu__title']
                # 不在菜单中显示权限管理，而是在header nav 中显示
                if title != u'权限管理':
                    menu_mapping[menu_id] = {
                        'title': title,
                        'icon': item['purview__menu__icon'],
                        'nodes': [
                            node
                        ]
                    }
    permission_menu_list = list()
    for k, v in sorted(menu_mapping.iteritems(), key=lambda t: t[0]):
        permission_menu_list.append(v) 
    request.session[settings.PERMISSION_SESSION_KEY] = permission_mapping
    request.session[settings.MENU_SESSION_KEY] = permission_menu_list

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        # Initial permission map
        initPermission(self.request, form.user_cache)
        return super(CustomLoginView, self).form_valid(form)

def image(request):
    verifyCode = VeifyCode()
    content, buf_str = verifyCode.getImage()
    request.session.pop('verify_code', '')
    request.session['verify_code'] = content
    return HttpResponse(buf_str, content_type='mage/png')

def verify(request):
    if request.method == 'POST':
        verify_code = request.session.get('verify_code', '')
        code = request.POST.get('verification_code', '')
        if verify_code != code.lower():
            return HttpResponse('false')
        else:
            return HttpResponse('true')

def verify_password(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if not user:
            return HttpResponse('false')
        else:
            return HttpResponse('true')

def tpl_download(request, filename, extension):
    tpl_path = os.path.join(settings.BASE_DIR, 'tpl', filename)
    content_type = mimetypes.guess_type(tpl_path)[0]
    response = FileResponse(open(tpl_path, 'rb'), content_type=content_type)
    response['Content-Disposition'] = 'attachment;filename={0}'.format(filename)
    return response
