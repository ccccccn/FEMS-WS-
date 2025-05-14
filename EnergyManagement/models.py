from django.db import models


# Create your models here.


class EnergyManageRank(models.Model):
    id = models.IntegerField(primary_key=True)
    call_time = models.IntegerField(default=0)
    call_rank = models.IntegerField(default=0)
    soc = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    soc_rank = models.IntegerField(default=0)

    class Meta:
        db_table = 'energy_manage_rank'
        verbose_name = '能量管理排名'