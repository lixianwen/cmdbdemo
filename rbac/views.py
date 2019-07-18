# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
from django.urls import reverse
from cmdb.utils import getAllURLs
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from models import Menu, Permission, Role, MyUser
from django.utils.module_loading import import_string
from django.views.decorators.http import require_POST
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from forms import AddMenuForm, SecondGradeMenuForm, PermissionForm, MultiPermissionForm, RoleForm

# Create your views here.

def customReverse(request, viewname, *args, **kwargs):
    url = reverse(viewname, *args, **kwargs)
    query_params = request.GET.get('source')
    if query_params:
        url = '{0}?{1}'.format(url, query_params)
    return url

def listMenu(request):
    menu_list = Menu.objects.all()
    menu_id = request.GET.get('mid')
    second_grade_menu_id = request.GET.get('sid')
    second_grade_menu_list = Permission.objects.filter(menu_id=menu_id) if menu_id else Permission.objects.none()
    not_menu_permission_list = Permission.objects.filter(related_id_id=second_grade_menu_id) if second_grade_menu_id else Permission.objects.none()
    add_menu_form = AddMenuForm()
    permission_form = PermissionForm()
    return render(request, 'rbac/menu_list.html', locals())

@require_POST
def addMenu(request):
    form = AddMenuForm(request.POST)
    if form.is_valid():
        new_object = form.save()
        return redirect(customReverse(request, 'rbac:list_menu'))

def editMenu(request, pk):
    menu = Menu.objects.get(id=pk)
    if request.method == 'POST':
        form = AddMenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return redirect(customReverse(request, 'rbac:list_menu'))
    else:
        form = AddMenuForm(instance=menu)
    return render(request, 'rbac/edit.html', locals())

def deleteMenu(request, pk):
    Menu.objects.get(id=pk).delete()
    return redirect(reverse('rbac:list_menu'))

def addSecondGradeMenu(request, mid):
    menu = Menu.objects.get(id=mid)
    form = SecondGradeMenuForm(initial={'menu': menu})
    if request.method == 'POST':
        form = SecondGradeMenuForm(request.POST)
        if form.is_valid():
            new_nemu = form.save()
            return redirect(customReverse(request, 'rbac:list_menu'))
    return render(request, 'rbac/add_second_menu.html', locals())

def editSecondGradeMenu(request, pk):
    perm = Permission.objects.get(id=pk)
    if request.method == 'POST':
        form = SecondGradeMenuForm(request.POST, instance=perm)
        if form.is_valid():
            form.save()
            return redirect(customReverse(request, 'rbac:list_menu'))
    else:
        form = SecondGradeMenuForm(instance=perm)
    return render(request, 'rbac/add_second_menu.html', locals())

def deleteSecondGradeMenu(request, pk):
    Permission.objects.get(id=pk).delete()
    return redirect(customReverse(request, 'rbac:list_menu'))

@require_POST
def addPermission(request, sid):
    second_grade_menu = Permission.objects.get(id=sid)
    form = PermissionForm(request.POST)
    if form.is_valid():
        form.instance.related_id = second_grade_menu
        new_object = form.save()
        return redirect(customReverse(request, 'rbac:list_menu'))

def editPermission(request, pk):
    perm = Permission.objects.get(id=pk)
    if request.method == 'POST':
        form = PermissionForm(request.POST, instance=perm)
        if form.is_valid():
            form.save()
            return redirect(customReverse(request, 'rbac:list_menu'))
    else:
        form = PermissionForm(instance=perm)
    return render(request, 'rbac/edit.html', locals())

def multiPermission(request):
    _type = request.GET.get('type', None)    # Type identify which form was posted

    # Get the app's url patterns which has installed
    url_dict = dict()
    urls = import_string(dotted_path=settings.ROOT_URLCONF)
    getAllURLs(urls.urlpatterns, url_dict, prefix='/')
    router_url_pattern_set = set(url_dict.keys())
    
    # Get the url info in database
    permission_dict = Permission.objects.exclude(url='/').values('id', 'url', 'url_pattern_name', 'description', 'menu', 'related_id')
    permission_url_pattern_set = set()
    for item in permission_dict:
        permission_url_pattern_set.add(item['url_pattern_name'])

    # Compare url_dict and permission_dict
    for item in permission_dict:
        router_obj = url_dict.get(item['url_pattern_name'], None)
        if router_obj is not None:
            if item['url'] != router_obj['url']:
                item['url'] = u'路由url和数据库中的url不一致'

    # URLs pattern should be added to database
    add_url_name_set = router_url_pattern_set - permission_url_pattern_set
    init_data = [value for key, value in url_dict.items() if key in add_url_name_set]
    PermissionAddFormSet = modelformset_factory(
        model=Permission,
        form=MultiPermissionForm,
        extra=len(init_data))
    if _type is not None and _type == 'add' and request.method == 'POST':
        formset_add = PermissionAddFormSet(request.POST, initial=init_data) 
        if formset_add.is_valid():
            formset_add.save()
            return redirect(customReverse(request, 'rbac:list_menu'))   
    else:
        formset_add = PermissionAddFormSet(
            initial=init_data,
            queryset=Permission.objects.none())
    
    # URLs pattern should be deleted from database
    delete_url_name_set = permission_url_pattern_set - router_url_pattern_set
    delete_url_list = [row for row in permission_dict if row['url_pattern_name'] in delete_url_name_set]

    # URLs pattern might be update to database
    might_update_url_set = permission_url_pattern_set & router_url_pattern_set
    update_queryset = Permission.objects.none()
    for update_item in permission_dict:
        url_name = update_item['url_pattern_name']
        if url_name in might_update_url_set:
            update_queryset = update_queryset.union(Permission.objects.filter(url_pattern_name=url_name))
    PermissionUpdateFormSet = modelformset_factory(
        model=Permission,
        form=MultiPermissionForm,
        extra=0)
    if _type is not None and _type == 'update' and request.method == 'POST':
        formset_update = PermissionUpdateFormSet(request.POST)
        if formset_update.is_valid():
            formset_update.save()
            return redirect(customReverse(request, 'rbac:list_menu'))
    else:
        formset_update = PermissionUpdateFormSet(queryset=update_queryset)

    return render(request, 'rbac/operate_multi_permission.html', locals())

class RoleList(ListView):
    model = Role

    def get_context_data(self, **kwargs):
        context = super(RoleList, self).get_context_data(**kwargs)
        context['form'] = RoleForm()
        return context

class RoleCreate(CreateView):
    model = Role
    form_class = RoleForm

class RoleUpdate(UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'rbac/edit.html'

class RoleDelete(DeleteView):
    model = Role
    success_url = reverse_lazy('rbac:list_role')

def assignPermission(request):
    user_id = request.GET.get('uid')
    user_list = MyUser.objects.all()
    if user_id is not None:
        user_obj = user_list.get(pk=user_id)
    else:
        user_obj = None

    role_id = request.GET.get('rid')
    role_list = Role.objects.all()
    if role_id is not None:
        role_obj = role_list.get(pk=role_id)
    else:
        role_obj = None

    user_roles = user_obj.role.all() if user_id else Role.objects.none()
    user_role_list = [i.id for i in user_roles] if user_roles else []

    # Save roles belong to user_obj
    if request.method == 'POST' and request.POST.get('type') == 'role':
        posted_role_list = request.POST.getlist('role')
        user_obj.role.set(posted_role_list)
        time.sleep(2)
        return redirect(request.get_full_path())

    # Save permissions belong to its role
    if request.method == 'POST' and request.POST.get('type') == 'permission':
        posted_permission_list = request.POST.getlist('permission')
        role_obj.purview.set(posted_permission_list)
        time.sleep(2)
        return redirect(request.get_full_path())

    # When chose a role, show all permissions belong to it,
    # otherwise to a user
    if role_obj:
        user_permission_list = [perm.id for perm in role_obj.purview.all()]
    elif user_obj:
        user_permission_list = [item['purview'] for item in user_obj.role.values('purview')]
    else:
        user_permission_list = list()

    # One grade menu
    all_menu_list = Menu.objects.values('id', 'title')
    all_menu_dict = dict()
    for item in all_menu_list:
        item['children'] = list()
        all_menu_dict[item['id']] = item

    # Second grade menu
    all_second_menu_list = Permission.objects.filter(menu__isnull=False).values('id', 'description', 'menu_id')
    all_second_menu_dict = dict()
    for s_item in all_second_menu_list:
        s_item['children'] = list()
        all_second_menu_dict[s_item['id']] = s_item
        menu_id = s_item['menu_id']
        all_menu_dict[menu_id]['children'].append(s_item)
        # all_menu_dict[menu_id] == all_menu_dict[item['id']]

    # All permissions which can not be menu
    all_permission_list = Permission.objects.filter(menu__isnull=True).values('id', 'description', 'related_id_id')
    for p_item in all_permission_list:
        related_id = p_item['related_id_id']
        if related_id is not None:
            all_second_menu_dict[related_id]['children'].append(p_item)
            # all_second_menu_dict[related_id] == all_second_menu_dict[s_item['id']] == s_item
            # all_menu_dict[menu_id]['children'].append(all_second_menu_dict[related_id])

    '''
    all_menu_list = <QuerySet [
        {
         'id': 1,
         'title': '资产管理',
         'children': [
             'id': 11,
             'description': '服务器列表',
             'menu_id': 1,
             'children': [
                 {
                  'id': 2,
                  'description': '编辑服务器',
                  'related_id_id': 11
                 }
             ]
         ]
        }
    ]>
    '''

    return render(request, 'rbac/assign_permission.html', locals())
