#!/usr/bin/env python
#coding:utf8

import re
import sys
from django.urls import reverse
from django.conf import settings
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.views.debug import technical_500_response
from django.contrib.auth.views import redirect_to_login

class UserExceptionMiddleware(object):
    '''在生产模式下，普通用户看到的是正常的错误页面，管理员或者在 INTERNAL_IPS 的 ip能看到详细的异常信息'''

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if request.user.is_superuser or request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
            return technical_500_response(request, *sys.exc_info())

class IPFilterMiddleware(object):
    '''限制只有在 INTERNAL_IPS 的 ip 能访问admin页面'''

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
        else:
            ip = request.META.get('REMOTE_ADDR')
        if request.path == '/admin/' and ip not in settings.INTERNAL_IPS:
            raise PermissionDenied
        response = self.get_response(request)
        return response

class RbacMiddleware(object):
    '''
    用户请求前验证用户权限
    '''
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        flag = False
        current_url = request.path

        for valid_url in settings.VALID_URL_LIST:
            if re.match(valid_url, current_url):
                # 白名单中的URL无需权限验证即可访问
                flag = True
                break

        if current_url == reverse('oauth2_provider:token'):
            flag = True

        request.breadcrumb_list = [
            {'title': u'首页', 'url': '/'}
        ]

        if not flag:
            permission_mapping = request.session.get(settings.PERMISSION_SESSION_KEY, False)
            if isinstance(permission_mapping, dict) and not permission_mapping:
                raise PermissionDenied
            elif not permission_mapping:
                return redirect_to_login(current_url)
            for description, item in permission_mapping.iteritems():
                reg = r'^{0}$'.format(item['url'])
                if re.match(reg, current_url):
                    flag = True
                    request.related_id = item['related_id']
                    if description == u'首页':
                        break
                    if request.related_id is not None:
                        request.breadcrumb_list.extend([
                            {'title': item['related_description'], 'url': item['related_url']},
                            {'title': description, 'url': item['url'], 'class': 'active'}
                        ])
                    else:
                        request.breadcrumb_list.append(
                            {'title': description, 'url': item['url'], 'class': 'active'}
                        )
                    break

        if not flag:
            raise PermissionDenied

        response = self.get_response(request)
        return response
