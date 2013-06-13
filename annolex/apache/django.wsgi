import os, sys
sys.path.append('/Library/WebServer/Documents/django')
os.environ['DJANGO_SETTINGS_MODULE'] = 'annolex.settings'
os.environ['PYTHON_EGG_CACHE'] = '/Library/WebServer/Documents/django/.python-eggs'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
