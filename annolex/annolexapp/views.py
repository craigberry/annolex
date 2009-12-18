from django.template import loader, Context
from django.http import HttpResponse
from annolex.annolexapp.models import AnnoLex, CorrectionForm, SearchForm
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import operator

def annolex(request):
    current_word = AnnoLex()
    word_list = None
    page = None

    searchform = SearchForm(request.session.get('searchform'))
    editform = CorrectionForm(request.session.get('editform'))

    annolex_session = request.session.get('annolex_session')
    if annolex_session:
        spelling_search = annolex_session['spelling_search']
        lemma_search = annolex_session['lemma_search']
        pos_search = annolex_session['pos_search']
        wordid_search = annolex_session['wordid_search']
        opchoice = annolex_session['opchoice']
    else:
        spelling_search = None
        lemma_search = None
        pos_search = None
        wordid_search = None
        opchoice = None

     
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
                request.session['editform'] = request.POST
                return HttpResponse("You must be logged in to save.")
            else:
                editform = CorrectionForm(request.POST)
                if editform.is_valid():
                    form = editform.save(commit=False)
                    form.corrected_by = request.user
                    form.save()

        elif request.POST.__getitem__('which_post') == 'Search':
            searchform = SearchForm(request.POST)
            request.session['searchform'] = request.POST
                
            spelling_search = request.POST.__getitem__('spelling')
            lemma_search = request.POST.__getitem__('lemma')
            pos_search = request.POST.__getitem__('pos')
            wordid_search = request.POST.__getitem__('wordid')
            opchoice = request.POST.__getitem__('opchoice')

            page = 1


    if not page and request.GET.get('page', '1') == 'last':
        page = request.GET.get('page', '1')
    else:
        if not page:
            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1

    qobj = []
    if spelling_search:
        qobj.append (Q(spelling__iregex=spelling_search))
    if lemma_search:
        qobj.append (Q(lemma__iregex=lemma_search))
    if pos_search:
        qobj.append (Q(pos__iregex=pos_search))
    if wordid_search:
        qobj.append (Q(wordid__iregex=wordid_search))

    if qobj:
        if opchoice and opchoice == '1':
            word_list = AnnoLex.objects.filter(reduce(operator.and_, qobj))
        else:
            word_list = AnnoLex.objects.filter(reduce(operator.or_, qobj))
    else:
        word_list = AnnoLex.objects.all()


    if word_list:
        paginator = Paginator(word_list, 25)
    
        try:
            words = paginator.page(page)
        except (EmptyPage, InvalidPage):
            words = paginator.page(paginator.num_pages)
    else:
        words = None


    request.session['annolex_session'] = { 'spelling_search': spelling_search,
                                           'lemma_search':    lemma_search,
                                           'pos_search':      pos_search,
                                           'wordid_search':   wordid_search,
                                           'opchoice':        opchoice }



    c = Context({ 'searchform': searchform,
                  'words': words, 
                  'editform': editform ,
                  'user': request.user,
                  'current_word': current_word })
    t = loader.get_template("annolex.html")
    return HttpResponse(t.render(c))


