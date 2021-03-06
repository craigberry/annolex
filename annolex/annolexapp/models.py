from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from django.db.models import permalink

class AnnoLex(models.Model):
    KwicL        = models.CharField(max_length=128)
    spelling     = models.CharField(max_length=40, db_index=True)
    KwicR        = models.CharField(max_length=128)
    lemma        = models.CharField(max_length=40, db_index=True)
    pos          = models.CharField(max_length=25, db_index=True)
    spellcolfreq = models.IntegerField()
    wordid       = models.CharField(max_length=45,primary_key=True)
    preselected  = models.BooleanField(default=0)
    citation     = models.CharField(max_length=30,db_index=True)

    def get_image_url(self):
        if not self.citation:
            return ''
        page = int(self.citation.partition('-')[0])
        doc = (self.wordid.partition('-')[0]).partition('_')[0]
        return '%s/%s-%05d' % (doc, doc, page)

    def get_textid(self):
         return self.wordid.partition('-')[0]

admin.site.register(AnnoLex)

# These are the correction operations that we log against the main class.
# Updates will be most common and represent a simple correction or
# annnotation.  An insert means a word is being split.  A delete means
# two are more words are being joined.

OPERATIONS = (
    (1, 'Update'),
    (2, 'Insert'),
    (3, 'Delete'),
)

STATUS_CHOICES = (
    (0, '(All)'),
    (1, 'Unapproved'),
    (2, 'Approved'),
    (3, 'Rejected'),
    (4, 'Held'),
)

class Correction(models.Model):
    operation       = models.IntegerField(choices=OPERATIONS, default=1)
    spelling_from   = models.CharField(max_length=45)
    spelling_to     = models.CharField(max_length=45, blank=True, null=True)
    lemma_from      = models.CharField(max_length=45)
    lemma_to        = models.CharField(max_length=45, blank=True, null=True)
    pos_from        = models.CharField(max_length=25)
    pos_to          = models.CharField(max_length=25, blank=True, null=True)
    wordid_from     = models.ForeignKey(AnnoLex, related_name='wordid_from')
    wordid_to       = models.CharField(max_length=45, blank=True, null=True)
    corrected_by    = models.ForeignKey(User, related_name='corrected_by')
    corrected_date  = models.DateTimeField(auto_now_add=True)
    status_by       = models.ForeignKey(User, related_name='status_by', blank=True, null=True)
    status_date     = models.DateTimeField(blank=True, null=True)
    applied_by      = models.ForeignKey(User, related_name='applied_by', blank=True, null=True)
    applied_date    = models.DateTimeField(blank=True, null=True)
    annotation      = models.TextField(blank=True, null=True)
    status          = models.IntegerField(choices=STATUS_CHOICES, default=1)

    class Meta:
        ordering = ('-corrected_date',)
        permissions = (
            ("can_review", "Can review corrections made by others"),
        )
        
    def __unicode__(self):
        return  "%s %s: %s (%s, %s) to %s (%s, %s)" %  (
                    self.wordid_from or "#%s" % self.id, 
                    self.get_operation_display(),
                    self.spelling_from, 
                    self.lemma_from, 
                    self.pos_from, 
                    self.spelling_to or self.spelling_from, 
                    self.lemma_to or self.lemma_from, 
                    self.pos_to or self.pos_from)
        
    @permalink
    def get_absolute_url(self):
        return('django.views.generic.list_detail.object_detail', None, {'object_id': self.id})
    
class CorrectionAdmin(admin.ModelAdmin):
    list_dislay = ('__unicode__', 'wordid_from', 'operation', 'spelling_from', 'spelling_to', 
                   'lemma_from', 'lemma_to', 'pos_from', 'pos_to')
    list_filter = ('corrected_by', 'corrected_date')

admin.site.register(Correction, CorrectionAdmin)

class CorrectionForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(CorrectionForm, self).__init__(*args, **kwargs)

        # change a widget attribute:
        self.fields['spelling_from'].widget.attrs["readonly"] = True
        self.fields['lemma_from'].widget.attrs["readonly"] = True
        self.fields['pos_from'].widget.attrs["readonly"] = True
        self.fields['wordid_from'].widget.attrs["readonly"] = True
        self.fields['spelling_from'].widget.attrs["size"] = 15
        self.fields['lemma_from'].widget.attrs["size"] = 15
        self.fields['pos_from'].widget.attrs["size"] = 10
        self.fields['spelling_to'].widget.attrs["size"] = 15
        self.fields['lemma_to'].widget.attrs["size"] = 15
        self.fields['pos_to'].widget.attrs["size"] = 10
        self.fields['annotation'].widget.attrs["cols"] = 30
        self.fields['annotation'].widget.attrs["rows"] = 8

    class Meta:
        model = Correction
        exclude = ('corrected_by', 'status')


class TextList(models.Model):
    textid     = models.CharField(max_length=12, primary_key=True)
    author     = models.CharField(max_length=25)
    title      = models.CharField(max_length=255)

    class Meta:
        ordering = ('author', 'title',)

    def __unicode__(self):
        author = self.author
        if author.find(',') > 0:
            author = author[:(self.author.find(',') + 3)] + '.'
        
        title_string = "%s: %s" % (author, self.title)
        title_len = len(title_string)
        if title_len > 52:
            return "%s...%s" % (title_string[0:30], title_string[title_len-20:])
        else:
            return title_string


# Now do the search form.

OPERATOR_CHOICES = (
    (1, 'and'),
    (2, 'or'),
)

SEARCH_SORT_CHOICES = (
    (1, 'Text Order'),
    (2, 'Lemma, POS, Spelling'),
    (3, 'Spelling, Lemma, POS'),
    (4, 'POS, Lemma, Spelling'),
)

SEARCH_MATCH_CHOICES = (
    (1, 'starting with'),
    (2, 'containing'),
)

SEARCH_FILTER_CHOICES = (
    (1, 'All'),
    (2, 'Preselected'),
)

class SearchForm(forms.Form):
    textid     = forms.ModelChoiceField(queryset=TextList.objects, required=False, label='Text', empty_label='(All)')
    spelling   = forms.CharField(max_length=45, required=False)
    lemma      = forms.CharField(max_length=45, required=False)
    pos        = forms.CharField(max_length=10, required=False, label='POS')
    citation   = forms.CharField(max_length=30, required=False, label='Citation')
    matchchoice = forms.ChoiceField(choices=SEARCH_MATCH_CHOICES, initial=1, required=False, label='Match')
    opchoice   = forms.ChoiceField(choices=OPERATOR_CHOICES, initial=1, required=False, label='Combine')
    sortchoice = forms.ChoiceField(choices=SEARCH_SORT_CHOICES, initial=1, required=False, label='Sort')
    filterchoice = forms.ChoiceField(choices=SEARCH_FILTER_CHOICES, initial=2, required=False, label='Filter')


FILTER_APPLIED_CHOICES = (
    (1, 'Unapplied'),
    (2, 'Applied'),
)


class ReviewChoicesForm(forms.Form):
    filterwho      = forms.ModelChoiceField(queryset=User.objects, required=False, label='Corrector', empty_label='(All)')
    filterstatus   = forms.ChoiceField(choices=STATUS_CHOICES, initial=1, required=True, label='Status')
    filterapplied  = forms.ChoiceField(choices=FILTER_APPLIED_CHOICES, initial=1, required=True, label='Applied')

