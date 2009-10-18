from django.conf.urls.defaults import *
from annolex.annolexapp.views import start, correction

urlpatterns = patterns('',
    url(r'^$', start),

)