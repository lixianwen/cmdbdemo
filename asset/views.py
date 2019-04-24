# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import xlrd
from django.urls import reverse
from cmdb.utils import validIPV4
from django.contrib import messages
from django.http import HttpResponse
from permission import check_permission
from rest_framework.response import Response
from django.shortcuts import render, redirect
from asset.serializers import AssetSerializer
from models import IDC, PhysicalServer, Asset
from django.http import Http404, JsonResponse
from rest_framework.exceptions import ValidationError
from forms import IdcForm, PhysicalServerForm, AssetForm
from rest_framework import status, viewsets, permissions
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

# Create your views here.

@check_permission
def idc(request):
    idc_list = IDC.objects.all()
    return render(request, 'asset/idc.html', locals())

@permission_required('asset.add_idc')
def addIDC(request):
    if request.method == 'POST':
        form = IdcForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            if IDC.objects.filter(name=name).exists():
                messages.add_message(request, messages.ERROR, u'{0} 已经存在'.format(name))
                return redirect(reverse('add_idc'))
            new_idc = form.save()
            messages.add_message(request, messages.SUCCESS, u'{0} 添加成功'.format(name))
            return redirect(reverse('idc'))
    else:
        form = IdcForm()
    return render(request, 'asset/add_idc.html', locals())

@permission_required('asset.change_idc')
def editIDC(request, pk):
    idc = IDC.objects.get(id=pk)
    if request.method == 'POST':
        form = IdcForm(request.POST, instance=idc)
        front_idc = idc.name
        if form.is_valid():
            name = form.cleaned_data['name']
            if front_idc != name:
                if IDC.objects.filter(name=name).exists():
                    messages.add_message(request, messages.ERROR, u'{0} 已经存在'.format(name))
                    return redirect(reverse('idc'))
            form.save()
            messages.add_message(request, messages.SUCCESS, u'{0} 修改成功'.format(name))
            return redirect(reverse('idc'))
    form = IdcForm(instance=idc)
    return render(request, 'asset/edit_idc.html', locals())

@permission_required('asset.delete_idc')
def delIDC(request, pk):
    IDC.objects.get(id=pk).delete()
    return redirect(reverse('idc'))

@check_permission
def physical_server(request):
    ps_list = PhysicalServer.objects.all()
    return render(request, 'asset/physical_server.html', locals())

@permission_required('asset.add_physicalserver')
def addPS(request):
    if request.method == 'POST':
        form = PhysicalServerForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            new_ps = form.save()
            messages.add_message(request, messages.SUCCESS, u'物理服务器添加成功')
            return redirect(reverse('ps'))
    else:
        form = PhysicalServerForm()
    return render(request, 'asset/add_ps.html', locals())

@permission_required('asset.change_physicalserver')
def editPS(request, pk):
    ps = PhysicalServer.objects.get(id=pk)
    if request.method == 'POST':
        form = PhysicalServerForm(request.POST, instance=ps)
        front_ps = ps.ip
        if form.is_valid():
            ip = form.cleaned_data['ip']
            if front_ps != ip:
                if PhysicalServer.objects.filter(ip=ip).exists():
                    messages.add_message(request, messages.ERROR, u'IP: {0} 已经存在'.format(ip))
                    return redirect(reverse('ps'))
            form.save()
            messages.add_message(request, messages.SUCCESS, u'物理服务器修改成功')
            return redirect(reverse('ps'))
    else:
        form = PhysicalServerForm(instance=ps)
    return render(request, 'asset/edit_ps.html', locals())

@permission_required('asset.delete_physicalserver')
def delPS(request, pk):
    PhysicalServer.objects.get(id=pk).delete()
    return redirect(reverse('ps'))

def ps_import(request):
    if request.method == 'POST':
        context = {
            'status': 'success',
            'message': u'导入成功'
        }
        ps_excel = request.FILES.get('file')
        try:
            t1 = xlrd.open_workbook(file_contents=ps_excel.file.read()).sheets()[0]
        except:
            context['status'] = 'field'
            context['message'] = u'文件损坏或文件类型错误，不能读取文件内容'
            messages.add_message(request, messages.ERROR, context['message'])
            return redirect(reverse('ps_import'))
        try:
            if t1:
                for row in xrange(1, t1.nrows):
                    manufacturer, model, sn, ip, cpu, memory, disk, nic_num, comment = t1.row_values(row)
                    PhysicalServer.objects.create(
                        manufacturer=manufacturer, 
                        model=model, 
                        sn=sn, 
                        ip=ip, 
                        cpu=cpu,
                        memory=memory,
                        disk=disk,
                        nic_num=int(nic_num),
                        comment=comment)
        except ValueError as e:
            context['status'] = 'field'
            context['message'] = u'第{0}行值类型错误（{1}），请修改后删除已导入成功的第1-{2}行，并重新上传'.format(row, e, row-1)
            messages.add_message(request, messages.ERROR, context['message'])
            return redirect(reverse('ps_import'))
        messages.add_message(request, messages.SUCCESS, u'导入成功')
        return redirect(reverse('ps'))
    tpl = 'ps_tpl.xlsx'      # template for import
    return render(request, 'asset/ps_import.html', {'tpl': tpl})

def ps_export(request):
    filename='export_ps.xlsx'
    export(filename=filename, model=PhysicalServer)
    return redirect(reverse('tpl', args=(filename,)))

def getPageList(totalPage, currentPage):
    '''
        每页显示5页
        总页数为偶数10页时，当前页前5页，当前页后4页
        总页数少于5页，显示所有页
        当前页少于当前页前，显示5页
        当前页大于总页数-当前页后（即最后那几页），显示最后那几页
        其他页数时递增显示5页
    '''
    displayPage = 5
    front = int(displayPage / 2)
    if displayPage % 2 == 1:
        behind = front
    else:
        behind = front - 1
    if totalPage < displayPage:
        return range(1, totalPage+1)
    elif currentPage <= front:
        return range(1, displayPage+1)
    elif currentPage >= totalPage - behind:
        start = totalPage - displayPage +1
        return range(start, totalPage+1)
    else:
        start = currentPage - front
        end = currentPage + behind
        return range(start, end+1)

def fenye(request, asset_list):
    paginator_obj = Paginator(asset_list, 3, 1)
    totalPage = paginator_obj.num_pages
    page = request.GET.get('page', 1)
    page_list = getPageList(totalPage, int(page))
    try:
        assets = paginator_obj.page(page)
    except PageNotAnInteger:
        assets = paginator_obj.page(1)
    except EmptyPage:
        assets = paginator_obj.page(paginator.num_pages)
    return assets, page_list

@check_permission
def listAsset(request):
    aname = request.GET.get('aname', '')
    atype = request.GET.get('atype', '')
    host = request.GET.get('host', '')
    env = request.GET.get('env', '')
    status = request.GET.get('status', '')
    queryset = Asset.objects.all()
    idc_list = IDC.objects.all()
    ps_list = PhysicalServer.objects.all()
    if aname:
        queryset = queryset.filter(idc_id=aname)
        if not queryset:
            asset_list = ''
    if atype:
        queryset = queryset.filter(asset_type=atype)
        if not queryset:
            asset_list = ''
    if host:
        queryset = queryset.filter(host_id=host)
        if not queryset:
            asset_list = ''
    if env:
        queryset = queryset.filter(env=env)
        if not queryset:
            asset_list = ''
    if status:
        queryset = queryset.filter(status=status)
        if not queryset:
            asset_list = ''
    if queryset:
        asset_list = queryset
    else:
        asset_list = Asset.objects.none()
    if request.method == 'POST':
        keyword = request.POST.get('keyword', '').strip()
        if keyword:
            asset_list = Asset.objects.filter(hostname__icontains=keyword)
            return render(request, 'asset/asset_list.html', locals())
        else:
            asset_list = fenye(request, asset_list.order_by('pk'))
            flag = 1
            return render(request, 'asset/asset_list.html', locals())
    if aname or atype or host or env or status:
        pass
    else:
        asset_list, page_list = fenye(request, asset_list.order_by('pk'))
        flag = 1
    return render(request, 'asset/asset_list.html', locals())
    
@permission_required('asset.add_asset')
def addAsset(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            new_asset = form.save()
            messages.add_message(request, messages.SUCCESS, u'主机添加成功')
            return redirect(reverse('list'))
    else:
        form = AssetForm()
    return render(request, 'asset/asset_add.html', locals())

@permission_required('asset.change_asset')
def editAsset(request, pk):
    asset = Asset.objects.get(id=pk)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        front_ip1 = asset.ip
        front_ip2 = asset.other_ip
        if form.is_valid():
            ip1 = form.cleaned_data['ip']
            ip2 = form.cleaned_data['other_ip']
            if ip1:
                if front_ip1 != ip1:
                    if Asset.objects.filter(ip=ip1).exists():
                        messages.add_message(request, messages.ERROR, u'IP: {0} 已经存在'.format(ip1))
                        return redirect(reverse('list'))
            if ip2:
                if front_ip2 != ip2:
                    if Asset.objects.filter(other_ip=ip2).exists():
                        messages.add_message(request, messages.ERROR, u'IP: {0} 已经存在'.format(ip2))
                        return redirect(reverse('list'))
            form.save()
            messages.add_message(request, messages.SUCCESS, u'主机信息修改成功')
            return redirect(reverse('list'))
    else:
        form = AssetForm(instance=asset)
    return render(request, 'asset/asset_edit.html', locals())

@permission_required('asset.delete_asset')
def delAsset(request, pk):
    Asset.objects.get(id=pk).delete()
    return redirect(reverse('list'))

@check_permission
def hostname(request):
    asset_list = Asset.objects.all()
    hostname_list = list()
    for i in asset_list:
        hostname_list.append(i.hostname)
    distinct_list = list(set(hostname_list))
    return JsonResponse(distinct_list, safe=False)

class AssetViewSet(viewsets.ModelViewSet):
    '''
    list: Return a list of all the existing assets

    create: Create a new asset instance via given data

    asset_env field mapping:
        1 ---> 生产环境
        2 ---> 测试环境

    asset_status field mapping:
        1 ---> 已使用
        2 ---> 未使用
        3 ---> 待回收
    
    ASSET_TYPE field mapping:
        1 ---> 虚拟机
        2 ---> 交换机
        3 ---> 路由器
        4 ---> 其他

    retrieve: Return an existing asset by giving primary key

    update: Update an existing asset instance via given data

    partial_update: This method has not yet supported for now

    destroy: Delete an existing asset by giving primary key

    '''

    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (permissions.IsAuthenticated, TokenHasReadWriteScope)

#    def get_queryset(self):
#        """
#        This view should return a list of all the assets in idc 稳速广州数据中心1
#        """
#        return Asset.objects.filter(idc=IDC.objects.get(name=u'稳速广州数据中心1'))

    def getValidatedData(self, obj):
        r = re.compile(r'get_(.*)_display')
        obj.validated_data['idc'] = IDC.objects.get(name=obj.validated_data['idc']['name'])
        obj.validated_data['host'] = PhysicalServer.objects.get(ip=obj.validated_data['host']['ip'])
        for k, v in obj.validated_data.iteritems():
            result = r.search(k)
            if result:
                obj.validated_data[result.group(1)] = obj.validated_data[k]
                tmp = obj.validated_data.pop(k)
        return obj

    def create(self, request):
        serializer = AssetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer = self.getValidatedData(serializer)
            ip1 = serializer.validated_data.get('ip')
            ip2 = serializer.validated_data.get('other_ip')
            if ip1:
                if Asset.objects.filter(ip=ip1).exists():
                    # pay attention to distinctions between rest_framework.exceptions.ValidationError and serializers.ValidationError
                    raise ValidationError({'ip': '{0} is exist.'.format(ip1)})
            if ip2:
                if Asset.objects.filter(other_ip=ip2).exists():
                    raise ValidationError({'other_ip': '{0} is exist.'.format(ip2)})
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def getObject(self, pk):
        try:
            return Asset.objects.get(pk=pk)
        except Asset.DoesNotExist:
            raise Http404

    def update(self, request, pk=None):
        asset = self.getObject(pk)
        front_ip1 = asset.ip
        front_ip2 = asset.other_ip
        serializer = AssetSerializer(asset, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer = self.getValidatedData(serializer)
            ip1 = serializer.validated_data.get('ip', '')
            ip2 = serializer.validated_data.get('other_ip', '')
            if ip1:
                if front_ip1 != ip1:
                    if Asset.objects.filter(ip=ip1).exists():
                        raise ValidationError({'ip': '{0} is exist.'.format(ip1)})
            if ip2:
                if front_ip2 != ip2:
                    if Asset.objects.filter(other_ip=ip2).exists():
                        raise ValidationError({'other_ip': '{0} is exist.'.format(ip2)})
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#    def partial_update(self, request, pk=None):
#        kwargs['partial'] = True
#        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        asset = self.getObject(pk)
        asset.delete()
        return Response(data={'ID': pk, 'status_code': 204, 'message': 'resource has been deleted'}, status=status.HTTP_204_NO_CONTENT)
