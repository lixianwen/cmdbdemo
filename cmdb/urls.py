"""cmdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))

"""

from views import *
from django.conf.urls import url
from django.contrib import admin
from views import CustomLoginView
from django.conf.urls import include
from django.views.static import serve
from django.contrib.auth.views import logout_then_login

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^asset/', include('asset.urls')),
    url(r'^salt/', include('salts.urls')),
    url(r'^zabbix/', include('zabbix.urls')),
    url(r'^permission/', include('rbac.urls', namespace='rbac')),
    url(r'^$', index, name='index'),
    url(r'login/$', CustomLoginView.as_view(), name='loginview'),
    url(r'^logout/$', logout_then_login, name='logoutview'),
    url(r'^image/$', image, name='image'),
    url(r'^verify/$', verify, name='verify'),
    url(r'^password/$', verify_password, name='password'),
    url(r'^tpl/(\w+.(xls|xlsx))$', tpl_download, name='tpl'),
    url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^(?P<path>favicon.ico)/$', serve, {
        'document_root': 'shared_static'
    }),
]
