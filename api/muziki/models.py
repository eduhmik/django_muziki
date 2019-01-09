from django.db import models

# Create your models here.
class Songz(models.Model):
    """class model for our api"""
    #song title
    title = models.CharField(max_length=255, null=False)
    #song artist
    artist = models.CharField(max_length=255, null=False)


    def __str__(self):
        return "{} - {}".format(self.title, self.artist)

