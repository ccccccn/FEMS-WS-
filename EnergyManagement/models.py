from django.db import models


# Create your models here.


class EnergyManageRank(models.Model):
    id = models.IntegerField(primary_key=True)
    call_time = models.IntegerField(default=0, null=True, blank=True)
    soc = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, null=True, blank=True)
    charge_time = models.IntegerField(default=0, null=True, blank=True)
    discharge_time = models.IntegerField(default=0, null=True, blank=True)
    recent_30days = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        db_table = 'energy_manage_rank'
        verbose_name = '能量管理排名'
