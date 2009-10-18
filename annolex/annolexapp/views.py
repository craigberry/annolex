from django.template import loader, Context
from django.http import HttpResponse
from annolex.annolexapp.models import AnnoLex, CorrectionForm
from django.core.paginator import Paginator, InvalidPage, EmptyPage

def start(request):
    word_list = AnnoLex.objects.all()
    paginator = Paginator(word_list, 25)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        words = paginator.page(page)
    except (EmptyPage, InvalidPage):
        words = paginator.page(paginator.num_pages)

    if request.method == 'POST' and request.POST.__getitem__('which_post') == 'Edit':
##        notes = request.raw_post_data
        wordid_from = request.POST.__getitem__('wordid_from')
        spelling_from = request.POST.__getitem__('spelling_from')
        lemma_from = request.POST.__getitem__('lemma_from')
        pos_from = request.POST.__getitem__('pos_from')
    else :
##        notes = ''
        wordid_from = ''
        spelling_from = ''
        lemma_from = ''
        pos_from = ''
        
    editform = CorrectionForm(initial={'wordid_from': wordid_from, 'lemma_from': lemma_from, 'spelling_from': spelling_from, 'pos_from': pos_from})
    c = Context({ 'words': words, 'editform': editform  })
    t = loader.get_template("start.html")
    return HttpResponse(t.render(c))

def correction(request):
    if request.method == 'POST' :
        form = CorrectionForm(request.POST)
        if form.is_valid():
            return render_to_response('start.html', {
                'form': form,
            })

