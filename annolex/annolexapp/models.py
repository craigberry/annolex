from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms

class AnnoLex(models.Model):
    KwicL        = models.CharField(max_length=128)
    spelling     = models.CharField(max_length=40)
    KwicR        = models.CharField(max_length=128)
    lemma        = models.CharField(max_length=40)
    pos          = models.CharField(max_length=10)
    spellcolfreq = models.IntegerField()
    wordid       = models.CharField(max_length=45,primary_key=True)

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

class Correction(models.Model):
    operation       = models.IntegerField(choices=OPERATIONS, default=1)
    spelling_from   = models.CharField(max_length=45)
    spelling_to     = models.CharField(max_length=45, blank=True, null=True)
    lemma_from      = models.CharField(max_length=45)
    lemma_to        = models.CharField(max_length=45, blank=True, null=True)
    pos_from        = models.CharField(max_length=10)
    pos_to          = models.CharField(max_length=10, blank=True, null=True)
    wordid_from     = models.CharField(max_length=45)
    wordid_to       = models.CharField(max_length=45, blank=True, null=True)
    corrected_by    = models.ForeignKey(User, related_name='corrected_by')
    corrected_date  = models.DateTimeField(auto_now_add=True)
    approved_by     = models.ForeignKey(User, related_name='approved_by', blank=True, null=True)
    approved_date   = models.DateTimeField(blank=True, null=True)
    applied_by      = models.ForeignKey(User, related_name='applied_by', blank=True, null=True)
    applied_date    = models.DateTimeField(blank=True, null=True)
    annotation      = models.TextField(blank=True, null=True)

admin.site.register(Correction)

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
         
    class Meta:
        model = Correction
        exclude = ('corrected_by')
