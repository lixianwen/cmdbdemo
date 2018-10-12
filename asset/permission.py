#!/usr/bin/env python
#coding:utf8

from django.urls import resolve
from django.core.exceptions import PermissionDenied

perm_dic = {
    'view_idc': ['idc', 'GET', []],
    'view_ps': ['ps', 'GET', []],
    'view_asset': ['list', 'GET', []],
    'search_asset': ['list', 'POST', []]
}

def check_user_perm(request, perm_key):
    if request.user.has_perm('asset.{0}'.format(perm_key)):
        #权限匹配成功且用户拥有此权限
        return True
    else:
        #权限匹配成功但用户无权限
        return False

def check_perm(request):
    url_object = resolve(request.path)
    urlname = url_object.url_name
    if urlname:
        for perm_key, mapping in perm_dic.iteritems():
            current_urlname, method, args = mapping
            if urlname == current_urlname:
                if request.method == method:
                    if args:
                        if request.method == 'GET':
                            return check_user_perm(request, perm_key)
                        else:
                            #POST方法
                            for i in args:
                                if i not in request.POST:
                                    #参数不全
                                    return False
                            #参数匹配成功
                            return check_user_perm(request, perm_key)
                    else:
                        return check_user_perm(request, perm_key)
        #urlname匹配不到权限
        return False
    else:
        #没有设置urlname
        return True 

def check_permission(function):
    def wrapper(request, *args, **kwargs):
        if check_perm(request):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrapper
