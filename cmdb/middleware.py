#!/usr/bin/env python
#coding:utf8

import sys
from django.conf import settings
from django.views.debug import technical_500_response
from django.core.exceptions import PermissionDenied

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
