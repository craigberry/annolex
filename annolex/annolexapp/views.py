from django.template import loader, Context
from django.http import HttpResponse
from annolex.annolexapp.models import AnnoLex

def start(request):
    words = AnnoLex.objects.all()
    t = loader.get_template("start.html")
    c = Context({ 'words': words })
    return HttpResponse(t.render(c))
