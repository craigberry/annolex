from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object
from annolex.annolexapp.views import annolex
from django.contrib.auth.views import login, logout
from annolex.annolexapp.models import Correction

display_correction_info = {'queryset': Correction.objects.all()}
create_correction_info = {'model': Correction}

urlpatterns = patterns('',
    url(r'^$', annolex),
    url(r'^accounts/login/$',  login),
    url(r'^accounts/logout/$', logout, {'next_page': '/annolex/'}),
    url(r'^review/$', object_list, dict(display_correction_info, allow_empty=True, paginate_by=25)),
    url(r'^review(?P<object_id>\d+)/$', object_detail, display_correction_info),
    url(r'^review/add/$', create_object, create_correction_info),
)

#urlpatterns += patterns('django.views.generic.simple',
#    url(r'^start/$', 'direct_to_template', {'template': 'start.html'}),
#)
