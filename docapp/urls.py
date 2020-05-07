from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'^doc/(?P<c_name>[^/]+)/(?P<room_name>[^/]+)/(?P<branch_name>[^/]+)/$', views.main, name='main'),
    re_path(r'^compare/(?P<c_name>[^/]+)/(?P<room_name>[^/]+)/$', views.compare, name='compare'),
    re_path(r'^history/(?P<c_name>[^/]+)/(?P<room_name>[^/]+)/$', views.history, name='history'),
    re_path(r'^push/(?P<c_name>[^/]+)/(?P<room_name>[^/]+)/(?P<branch_name>[^/]+)/$', views.push, name='push'),
    re_path(r'^pull/(?P<c_name>[^/]+)/(?P<room_name>[^/]+)/(?P<branch_name>[^/]+)/$', views.pull, name='pull'),
    re_path(r'^PRS/(?P<c_name>[^/]+)/(?P<room_name>[^/]+)/(?P<branch_name>[^/]+)/$', views.pull_requests, name='pull_requests'),
    path('save', views.saveit, name='saveit'),
]