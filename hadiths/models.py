from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class HadithSource(models.Model):
    name = models.CharField(max_length=255)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sources = models.ManyToManyField(HadithSource, through='ProfileHadithSource')

class ProfileHadithSource(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    hadith_source = models.ForeignKey(HadithSource, on_delete=models.CASCADE)
    hadiths_read_number = models.IntegerField(default=0)

class Hadith_Read(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hadith_number = models.IntegerField()


class Hadith(models.Model):
    hadith_id = models.AutoField(primary_key=True)
    source = models.ForeignKey(HadithSource, on_delete=models.CASCADE)
    chapter_no = models.IntegerField()
    hadith_no = models.IntegerField()
    chapter = models.CharField(max_length=255)
    chain_indx = models.CharField(max_length=255)
    text_ar = models.TextField()
    text_en = models.TextField()

    @property
    def get_absolute_url(self):
        return reverse('singlehadith', kwargs={'hadith_id': self.hadith_id})


class ProfileHadith(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    hadith = models.ForeignKey(Hadith, on_delete=models.CASCADE)