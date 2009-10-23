from django.conf.urls.defaults import *
from annolex.annolexapp.views import start, correction
from django.contrib.auth.views import login, logout

urlpatterns = patterns('',
    url(r'^$', start),
    (r'^accounts/login/$',  login),
    (r'^accounts/logout/$', logout, {'next_page': '/annolex/'}),

)