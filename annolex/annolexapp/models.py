from django.db import models
from django.contrib import admin

class AnnoLex(models.Model):
    KwicL = models.CharField(max_length=128)
    spell = models.CharField(max_length=40)
    KwicR = models.CharField(max_length=128)
    lempos = models.CharField(max_length=40)
    spellcolfreq = models.IntegerField()
    wordid = models.CharField(max_length=45,primary_key=True)

admin.site.register(AnnoLex)
