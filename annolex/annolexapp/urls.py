from django.conf.urls.defaults import *
from annolex.annolexapp.views import start

urlpatterns = patterns('',
    url(r'^$', start),
)