from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^add/$', add, name='ADD'),
    url(r'^del/$', delete, name='delete'),
]
