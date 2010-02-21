from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object
from django.views.generic.simple import direct_to_template
from annolex.annolexapp.views import annolex, review
from django.contrib.auth.views import login, logout
from annolex.annolexapp.models import Correction


urlpatterns = patterns('',
    url(r'^$', annolex),
    url(r'^accounts/login/$',  login),
    url(r'^accounts/logout/$', logout, {'next_page': '/annolex/'}),
    url(r'^review/$', review),
    url(r'^about/$', direct_to_template, {'template': 'about.html'}),
)

#urlpatterns += patterns('django.views.generic.simple',
#    url(r'^start/$', 'direct_to_template', {'template': 'start.html'}),
#)
