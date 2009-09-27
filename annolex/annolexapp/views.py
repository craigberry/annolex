from django.template import loader, Context
from django.http import HttpResponse
from annolex.annolexapp.models import AnnoLex
from django.core.paginator import Paginator, InvalidPage, EmptyPage

def start(request):
    word_list = AnnoLex.objects.all()
    paginator = Paginator(word_list, 30)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        words = paginator.page(page)
    except (EmptyPage, InvalidPage):
        words = paginator.page(paginator.num_pages)

    t = loader.get_template("start.html")
    c = Context({ 'words': words })
    return HttpResponse(t.render(c))
