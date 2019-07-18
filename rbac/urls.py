from django.conf.urls import url, include
from views import *


urlpatterns = [
    url(r'^menu/list/$', listMenu, name='list_menu'),
    url(r'^menu/add/$', addMenu, name='add_menu'),
    url(r'^menu/edit/(?P<pk>\d+)/$', editMenu, name='edit_menu'),
    url(r'^menu/delete/(?P<pk>\d+)/$', deleteMenu, name='delete_menu'),
    url(r'^second/menu/add/(?P<mid>\d+)/$', addSecondGradeMenu, name='add_second_menu'),
    url(r'^second/menu/edit/(?P<pk>\d+)/$', editSecondGradeMenu, name='edit_second_menu'),
    url(r'^second/menu/delete/(?P<pk>\d+)/$', deleteSecondGradeMenu, name='delete_second_menu'),
    url(r'^add/(?P<sid>\d+)/$', addPermission, name='add_permission'),
    url(r'^edit/(?P<pk>\d+)/$', editPermission, name='edit_permission'),
    url(r'^delete/(?P<pk>\d+)/$', deleteSecondGradeMenu, name='delete_permission'),
    url(r'multi/permissions/$', multiPermission, name='multi-permission'),
    url(r'^role/list/$', RoleList.as_view(), name='list_role'),
    url(r'^role/add/$', RoleCreate.as_view(), name='add_role'),
    url(r'^role/edit/(?P<pk>\d+)/$', RoleUpdate.as_view(), name='edit_role'),
    url(r'^role/delete/(?P<pk>\d+)/$', RoleDelete.as_view(), name='delete_role'),
    url(r'^assign/permissions/$', assignPermission, name='assign-permission'),
]
