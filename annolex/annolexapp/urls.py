from django.conf.urls.defaults import *
from annolex.annolexapp.views import annolex
from django.contrib.auth.views import login, logout

urlpatterns = patterns('',
    url(r'^$', annolex),
    url(r'^accounts/login/$',  login),
    url(r'^accounts/logout/$', logout, {'next_page': '/annolex/'}),
)

#urlpatterns += patterns('django.views.generic.simple',
#    url(r'^start/$', 'direct_to_template', {'template': 'start.html'}),
#)
