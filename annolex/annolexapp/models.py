from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

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
    (1, 'UPDATE'),
    (2, 'INSERT'),
    (3, 'DELETE'),
)

class Correction(models.Model):
    operation       = models.IntegerField(choices=OPERATIONS, default=1)
    spelling_from   = models.CharField(max_length=45)
    spelling_to     = models.CharField(max_length=45)
    lemma_from      = models.CharField(max_length=45)
    lemma_to        = models.CharField(max_length=45)
    pos_from        = models.CharField(max_length=10)
    pos_to          = models.CharField(max_length=10)
    wordid_from     = models.CharField(max_length=45)
    wordid_to       = models.CharField(max_length=45)
    corrected_by    = models.ForeignKey(User, related_name='corrected_by')
    corrected_date  = models.DateTimeField(auto_now_add=True)
    approved_by     = models.ForeignKey(User, related_name='approved_by')
    approved_date   = models.DateTimeField()
    applied_by      = models.ForeignKey(User, related_name='applied_by')
    applied_date    = models.DateTimeField()
    annotation      = models.TextField()

admin.site.register(Correction)
    
