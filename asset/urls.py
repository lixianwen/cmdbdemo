from django.conf.urls import url, include
from views import *
from rest_framework.routers import SimpleRouter
from rest_framework.documentation import include_docs_urls

# Create a router and register our viewsets with it.
router = SimpleRouter()
router.register(r'api', AssetViewSet, base_name='asset')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^idc/$', idc, name='idc'),
    url(r'^idc/add/$', addIDC, name='add_idc'),
    url(r'^idc/edit/$', editIDC, name='edit_idc'),
    url(r'^idc/del/$', delIDC, name='del_idc'),
    url(r'^ps/$', physical_server, name='ps'),
    url(r'^ps/add/$', addPS, name='add_ps'),
    url(r'^ps/edit/$', editPS, name='edit_ps'),
    url(r'^ps/del/$', delPS, name='del_ps'),
    url(r'^list/$', listAsset, name='list'),
    url(r'^add/$', addAsset, name='add'),
    url(r'^edit/$', editAsset, name='edit'),
    url(r'^del/$', delAsset, name='del'),
    url(r'^hostname/$', hostname, name='hostname'),
    url(r'^docs/', include_docs_urls(
                            title='Asset API Documentation', 
                            description='This viewset automatically provides `list`, `create`, `retrieve`, `update` and `destroy` actions',
                        )
    ),
]

# Generic Error Views for API-only application
#handler500 = 'rest_framework.exceptions.server_error'
#handler400 = 'rest_framework.exceptions.bad_request'
