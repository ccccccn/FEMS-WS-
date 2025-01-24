from django.db import models

# Create your models here.
class WeiboHotPointSearch(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    play = models.IntegerField()
    url = models.URLField()

    def __str__(self):
        return self.title
