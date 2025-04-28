from django.db import models


# Create your models here.
class PLC(models.Model):
    name = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    slot = models.IntegerField()
    rack = models.IntegerField()
    starts = models.IntegerField()
    length = models.IntegerField()


class DataPoint(models.Model):
    plc = models.ForeignKey(PLC, on_delete=models.CASCADE)
    point_id = models.IntegerField()
    is_forward = models.BooleanField()
    is_storage = models.BooleanField()
    is_display = models.BooleanField()
