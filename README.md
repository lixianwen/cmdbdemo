# 一个简单的CMDB Demo
###### 前端使用[zui框架](http://zui.sexy/)、javascript、jquery和jquery ui
###### 后端使用python、Django框架 和 Django Rest 框架 还有一些优秀的第三方包，例如 [`django-oauth-toolkit`](https://django-oauth-toolkit.readthedocs.io/en/latest/index.html) 和 [`django-widget-tweaks`](https://pypi.org/project/django-widget-tweaks/)

### 开发环境：
python 2.7.5  
理论上python 3.6 也支持，不过我没做兼容性测试

### 安装：
`pip install -r requirements`

**注意：salt-api 需要单独安装和配置**

### 配置文件
`/path/to/cmdbdemo/cdb.conf`  
编辑文件设置服务相关的帐号密码  

### 项目组成
- 主机管理
- Asset API
- 使用Saltstack API 批量做一些工作
- 使用Zabbix API 添加或删除主机

#### 1. Asset
主机管理部分为**机房**、**物理服务器**和**虚拟机**。信息使用表格展示，支持增删改查操作

#### 2. Salts
这部分使用salt-httpapi 启动一个salt-api服务，然后调用API 完成一些批量操作  
参考文档：[rest_cherrypy](https://docs.saltstack.com/en/latest/ref/netapi/all/salt.netapi.rest_cherrypy.html)

把`/path/to/cmdbdemo/salts/files` 里的内容拷贝到任何你想放置的地方，修改saltstack 的配置文件中的`file_roots` 和 `/path/to/cmdbdemo/cmdb/settings.py` 中的`MEDIA_ROOT`

#### 3. zabbix
使用Zabbix API 添加或删除主机  
不支持添加代理主机，但是在`zabbixapi.py` 预留了接口  
参考文档：[zabbix host interface](https://www.zabbix.com/documentation/3.4/zh/manual/api/reference/hostinterface)

#### 4. Asset API
使用[Django REST framework](https://www.django-rest-framework.org/) 开发的API，支持检索所有主机（分页显示，每页5条记录）、检索单个主机、创建主机、更新主机和删除主机。restful风格。  

其他特性：
- 身份验证和权限检查基于`oauth2`
- 请求速率限制为每分钟10次，每天14400次
- 默认返回`json`格式数据，使用URL 关键字参数`?format=api` 返回html
- 自定义异常和一些自定义的验证

示例代码
```
In [75]: headers = {'Authorization': 'Bearer J2XIhYfhn7on90eXFcsOjOie09vNae'}

In [76]: requests.get(url='http://192.168.0.125:8000/asset/api/1/', headers=headers).text
Out[76]: u'{"url":"http://192.168.0.125:8000/asset/api/1/","ip":"192.168.0.127","other_ip":"192.168.0.13","idc_name":"\u7a33\u901f\u6c55\u5c3e\u6570\u636e\u4e2d\u5fc31","hostname":"","cpu":"","memory":"","disk":"","system":"","status":"\u5df2\u4f7f\u7528","asset_type":"\u865a\u62df\u673a","env":"\u6d4b\u8bd5\u73af\u5883","belong_to":"192.168.0.20","comment":""}'
```
也可以使用应用程序接口，而不是直接使用网络接口与API 进行交互。[参考文档](https://www.django-rest-framework.org/topics/api-clients/)
