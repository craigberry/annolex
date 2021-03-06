from django.template import loader, Context
from django.http import HttpResponse
from annolex.annolexapp.models import AnnoLex, CorrectionForm, SearchForm, Correction, ReviewChoicesForm, TextList
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
import operator

import json
from django.db import connection

def annolex(request):
    current_word = AnnoLex()
    word_list = None
    page = None

    searchform = SearchForm(request.session.get('searchform'))
    editform = CorrectionForm(request.session.get('editform'))

    annolex_session = request.session.get('annolex_session')
    if annolex_session:
        text_search = annolex_session['text_search']
        spelling_search = annolex_session['spelling_search']
        lemma_search = annolex_session['lemma_search']
        pos_search = annolex_session['pos_search']
        citation_search = annolex_session['citation_search']
        matchchoice = annolex_session['matchchoice']
        opchoice = annolex_session['opchoice']
        sortchoice = annolex_session['sortchoice']
        filterchoice = annolex_session['filterchoice']
    else:
        text_search = None
        spelling_search = None
        lemma_search = None
        pos_search = None
        citation_search = None
        matchchoice = None
        opchoice = None
        sortchoice = None
        filterchoice = None


     
    if request.method == 'POST':
        if request.POST.__getitem__('which_post') == 'Edit':

            wordid_from = request.POST.__getitem__('wordid_from')
            spelling_from = request.POST.__getitem__('spelling_from')
            lemma_from = request.POST.__getitem__('lemma_from')
            pos_from = request.POST.__getitem__('pos_from')
            citation = request.POST.__getitem__('citation')
            
            current_word.wordid = wordid_from
            current_word.spelling = spelling_from
            current_word.lemma = lemma_from
            current_word.pos = pos_from
            current_word.citation = citation
            textid = current_word.wordid.partition('-')[0]
            text_name = TextList.objects.get(textid=textid).title
            current_word.text_name = text_name

            editform = CorrectionForm(initial={'wordid_from': wordid_from, 
                                               'lemma_from': lemma_from, 
                                               'spelling_from': spelling_from, 
                                               'pos_from': pos_from,
                                               'citation': citation,
                                               'text_name': text_name})

        elif request.POST.__getitem__('which_post') == 'Save':
            if not request.user.is_authenticated():
                request.session['editform'] = request.POST
                return HttpResponse("You must be logged in to save.")
            else:
                editform = CorrectionForm(request.POST)
                if editform.is_valid():
                    form = editform.save(commit=False)
                    form.corrected_by = request.user
                    form.status = 1
                    form.save()

        elif request.POST.__getitem__('which_post') == 'Search':
            searchform = SearchForm(request.POST)
            request.session['searchform'] = request.POST
                
            text_search = request.POST.__getitem__('textid')
            spelling_search = request.POST.__getitem__('spelling')
            lemma_search = request.POST.__getitem__('lemma')
            pos_search = request.POST.__getitem__('pos')
            citation_search = request.POST.__getitem__('citation')
            matchchoice = request.POST.__getitem__('matchchoice')
            opchoice = request.POST.__getitem__('opchoice')
            sortchoice = request.POST.__getitem__('sortchoice')
            filterchoice = request.POST.__getitem__('filterchoice')

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
    if matchchoice and matchchoice == '2':
        if spelling_search:
            qobj.append (Q(spelling__icontains=spelling_search))
        if lemma_search:
            qobj.append (Q(lemma__icontains=lemma_search))
        if pos_search:
            qobj.append (Q(pos__icontains=pos_search))
    else:
        if spelling_search:
            qobj.append (Q(spelling__istartswith=spelling_search))
        if lemma_search:
            qobj.append (Q(lemma__istartswith=lemma_search))
        if pos_search:
            qobj.append (Q(pos__istartswith=pos_search))
            
     # Yes, wordid.  Because the wordid starts with the text ID, this should work.
    if text_search:
        qobj.append (Q(wordid__istartswith=text_search))
    if citation_search:
        qobj.append (Q(citation__istartswith=citation_search))

    if qobj:
        order_by_list= ('wordid',)
        if sortchoice == '2':
            order_by_list = ('lemma' , 'pos', 'spelling')
        elif sortchoice == '3':
            order_by_list = ('spelling', 'lemma', 'pos')
        elif sortchoice == '4':
            order_by_list = ('pos', 'lemma', 'spelling')
        
        if filterchoice and filterchoice == '2':
            if opchoice and opchoice == '1':
                word_list = AnnoLex.objects.filter(preselected=1).filter(reduce(operator.and_, qobj)).order_by(*order_by_list)[:2500]
            else:
                word_list = AnnoLex.objects.filter(preselected=1).filter(reduce(operator.or_, qobj)).order_by(*order_by_list)[:2500]
        else:
            if opchoice and opchoice == '1':
                word_list = AnnoLex.objects.filter(reduce(operator.and_, qobj)).order_by(*order_by_list)[:2500]
            else:
                word_list = AnnoLex.objects.filter(reduce(operator.or_, qobj)).order_by(*order_by_list)[:2500]


    if word_list:
        paginator = Paginator(word_list, 25)
    
        try:
            words = paginator.page(page)
        except (EmptyPage, InvalidPage):
            words = paginator.page(paginator.num_pages)
    else:
        words = None


    request.session['annolex_session'] = { 'text_search':     text_search,
                                           'spelling_search': spelling_search,
                                           'lemma_search':    lemma_search,
                                           'pos_search':      pos_search,
                                           'citation_search': citation_search,
                                           'matchchoice':     matchchoice,
                                           'opchoice':        opchoice,
                                           'sortchoice':      sortchoice ,
                                           'filterchoice':      filterchoice }



    c = Context({ 'searchform': searchform,
                  'words': words, 
                  'editform': editform ,
                  'user': request.user,
                  'current_word': current_word })
    t = loader.get_template("annolex.html")
    return HttpResponse(t.render(c))

####

def getcounts(request):

    eebo_id = request.GET.get('eebo_id', 'ERROR: MISSING EEBOID')

    sql = "select substring_index(wordid, '-', 1) as eebo_id, count(*) as num_defects " \
          + "from annolexapp_annolex where preselected = 1 and wordid like %s " \
          + "group by substring_index(wordid, '-', 1);"

    cursor = connection.cursor()
    cursor.execute(sql, eebo_id + "-%")
    row = cursor.fetchone()
    cursor.close()

    if row is None:
        eebo_id = "Invalid"
        defects_remaining = 0
    else:
        defects_remaining = row[1]

    return HttpResponse(json.dumps({"volume": eebo_id, "defects_remaining": defects_remaining}))

####

def review(request):
    current_correction = Correction()
    correction_list = None
    page = None

    reviewchoicesform = ReviewChoicesForm(request.session.get('reviewchoicesform'))

    annolex_review_session = request.session.get('annolex_review_session')
    if annolex_review_session:
        filterwho = annolex_review_session['filterwho']
        filterstatus = annolex_review_session['filterstatus']
        filterapplied = annolex_review_session['filterapplied']
    else:
        filterwho = None
        filterstatus = 1
        filterapplied = None

     
    if request.method == 'POST':
        which_post = request.POST.__getitem__('which_post')
        if 'Status' in which_post:
            if not (request.user.is_authenticated() and  'annolexapp.can_review' in request.user.get_all_permissions()):
                return HttpResponse("You must be logged in and have review permission to approve corrections.")

            correction_id = request.POST.__getitem__('id')
            status = 0
            if which_post == 'Status_Unapproved':
                status = 1
            if which_post == 'Status_Approved':
                status = 2
            if which_post == 'Status_Rejected':
                status = 3
            if which_post == 'Status_Held':
                status = 4
            
            current_correction = Correction(correction_id)
            record_status(current_correction, status, request.user.id)

        elif which_post == 'Filter':
            reviewchoicesform = ReviewChoicesForm(request.POST)
            request.session['reviewchoicesform'] = request.POST
                
            filterwho = request.POST.__getitem__('filterwho')
            filterstatus = request.POST.__getitem__('filterstatus')
            filterapplied = request.POST.__getitem__('filterapplied')

            page = 1
        else:
            return HttpResponse("unknown post type: " + which_post)

    if not page and request.GET.get('page', '1') == 'last':
        page = request.GET.get('page', '1')
    else:
        if not page:
            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1

    qobj = []
    if filterwho:
            qobj.append (Q(corrected_by__exact=filterwho))

    if filterstatus and filterstatus <> '0':
            qobj.append (Q(status=filterstatus))

    if filterapplied and filterapplied == '2':
            qobj.append (Q(applied_date__isnull=False))
    else:
            qobj.append (Q(applied_date__isnull=True))

    if qobj:
        correction_list = Correction.objects.filter(reduce(operator.and_, qobj)).order_by('-corrected_date')[:2500]
    else:
        correction_list = Correction.objects.order_by('-corrected_date')[:2500]


    if correction_list:
        paginator = Paginator(correction_list, 25)
    
        try:
            corrections = paginator.page(page)
        except (EmptyPage, InvalidPage):
            corrections = paginator.page(paginator.num_pages)
    else:
        corrections = None


    request.session['annolex_review_session'] = { 'filterwho':      filterwho,
                                                  'filterstatus': filterstatus,
                                                  'filterapplied':  filterapplied }


    c = Context({ 'reviewchoicesform': reviewchoicesform,
                  'corrections': corrections, 
                  'user': request.user,
                  'current_correction': current_correction })
    t = loader.get_template("review.html")
    return HttpResponse(t.render(c))

def record_status(correction, status, user_id):
    from django.db import connection, transaction

    cursor = connection.cursor()
    sql = "UPDATE annolexapp_correction SET status_by_id = %s, status_date = now(), status=%s WHERE id = %s"
    cursor.execute(sql, [user_id, status, correction.id])

    if correction.operation == 1 and status == 2: # Update
    
        sql = '''UPDATE  annolexapp_annolex a
INNER JOIN annolexapp_correction c
ON a.wordid = c.wordid_from_id
SET spelling = CASE WHEN LENGTH(c.spelling_to) > 0 THEN c.spelling_to ELSE a.spelling END,
lemma = CASE WHEN LENGTH(c.lemma_to) > 0 THEN c.lemma_to ELSE a.lemma END,
pos = CASE WHEN LENGTH(c.pos_to) > 0 THEN c.pos_to ELSE a.pos END,
preselected = 0
WHERE c.id = %s
'''
        cursor.execute(sql, [correction.id])

    transaction.commit_unless_managed()

####

@permission_required('annolexapp.can_review')
def get_approved_corrections(request):
    import time
    import csv
    from django.utils.encoding import force_bytes
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="annolex_corrections_' \
                                      + time.strftime("%Y%m%d%H%m") + '.csv"'

    writer = csv.writer(response, delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None, escapechar="\\")

    sql = "SELECT CASE c.operation " \
           + "  WHEN 1 THEN 'UPDATE' " \
           + "  WHEN 2 THEN 'INSERT' " \
           + "  WHEN 3 THEN 'DELETE' " \
           + "END AS operation,  " \
           + "c.spelling_from, c.spelling_to,  " \
           + "c.lemma_from, c.lemma_to,  " \
           + "c.pos_from, c.pos_to, " \
           + "c.wordid_from_id, c.wordid_to,  " \
           + "u.username AS corrector, " \
           + "CAST(c.corrected_date AS char) AS corrected_date, " \
           + "u2.username AS approver, " \
           + "CAST(c.status_date AS char) AS approved_date, " \
           + "REPLACE(annotation, '\r\n', '|') AS annotation " \
    + "FROM annolexapp_correction c " \
    + "INNER JOIN auth_user u " \
    + "ON u.id = c.corrected_by_id " \
    + "INNER JOIN auth_user u2 " \
    + "ON u2.id = c.status_by_id " \
    + "WHERE c.status = 2 -- approved " \
    + "  AND c.applied_date IS NULL; "

    cursor = connection.cursor()
    cursor.execute(sql)

    col_names = [desc[0] for desc in cursor.description]
    writer.writerow(col_names)

    for row in cursor.fetchall():
        writer.writerow([force_bytes(s, "utf-8").decode("utf-8").encode("utf-8") for s in row])
        
    cursor.close()

    return response
####

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.forms import EmailField
from django.utils.translation import ugettext_lazy as _

class UserCreationForm(UserCreationForm):
    email = EmailField(label=_("Email address"), required=True)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
 
    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/accounts/login/")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })
