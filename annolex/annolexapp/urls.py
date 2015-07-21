from django.conf.urls import patterns, url, include
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from annolex.annolexapp.views import annolex, review, getcounts
from annolex.annolexapp.views import get_approved_corrections, register
from django.contrib.auth.views import login, logout
from annolex.annolexapp.models import Correction
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', annolex),
    url(r'^accounts/login/$',  login),
    url(r'^accounts/logout/$', logout, {'next_page': '/'}),
    url(r'^review/$', review),
    url(r'^about/$', TemplateView.as_view(template_name='about.html')),
    url(r'^defects/(?P<path>.*)$', TemplateView.as_view(template_name='defects.html')),
    url(r'^getcounts/$', getcounts),
    url(r'^get_approved_corrections/$', get_approved_corrections),
    url(r'^register/$', register),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

#urlpatterns += patterns('django.views.generic.simple',
#    url(r'^start/$', 'direct_to_template', {'template': 'start.html'}),
#)
