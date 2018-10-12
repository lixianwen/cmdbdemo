from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^collect/$', collect, name='collect'),
    url(r'^command/$', command, name='command'),
    url(r'^install/$', install, name='install'),
    url(r'^upload/$', upload, name='upload'),
    url(r'^push/$', push, name='push'),
    url(r'^job/$', job, name='job'),
    url(r'^script/$', script, name='script'),
]
