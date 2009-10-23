from django.template import loader, Context
from django.http import HttpResponse
from annolex.annolexapp.models import AnnoLex, CorrectionForm
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

def start(request):
    word_list = AnnoLex.objects.all()
    paginator = Paginator(word_list, 25)
    current_word = AnnoLex()

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        words = paginator.page(page)
    except (EmptyPage, InvalidPage):
        words = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        if request.POST.__getitem__('which_post') == 'Edit':
            wordid_from = request.POST.__getitem__('wordid_from')
            spelling_from = request.POST.__getitem__('spelling_from')
            lemma_from = request.POST.__getitem__('lemma_from')
            pos_from = request.POST.__getitem__('pos_from')
            
            current_word.wordid = wordid_from
            current_word.spelling = spelling_from
            current_word.lemma = lemma_from
            current_word.pos = pos_from

            editform = CorrectionForm(initial={'wordid_from': wordid_from, 
                                               'lemma_from': lemma_from, 
                                               'spelling_from': spelling_from, 
                                               'pos_from': pos_from})

        elif request.POST.__getitem__('which_post') == 'Save':
            if not request.user.is_authenticated():
                return HttpResponse("You must be logged in to save.")
            else:
                editform = CorrectionForm(request.POST)
                if editform.is_valid():
                    form = editform.save(commit=False)
                    form.corrected_by = request.user
                    form.save()
    else:
        editform = CorrectionForm()
        
    c = Context({ 'words': words, 
                  'editform': editform ,
                  'user': request.user,
                  'current_word': current_word })
    t = loader.get_template("start.html")
    return HttpResponse(t.render(c))

def correction(request):
    if request.method == 'POST' :
        form = CorrectionForm(request.POST)
        if form.is_valid():
            return render_to_response('start.html', {
                'form': form,
            })

