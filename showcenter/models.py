from django.db import models


# Create your models here.

class PieDistribution(models.Model):
    PIE_TYPE_CHOICES = [
        ('Soc_distribution', 'Soc distribution'),
        ('Frequency_Distribution', 'Frequency Distribution'),
        ('Duration_distribution', 'Duration Distribution')
    ]
    analysis_time = models.DateTimeField(auto_now_add=True)
    partition1 = models.DecimalField(decimal_places=2, max_digits=4)
    partition2 = models.DecimalField(decimal_places=2, max_digits=4)
    partition3 = models.DecimalField(decimal_places=2, max_digits=4)
    partition4 = models.DecimalField(decimal_places=2, max_digits=4)
    partition5 = models.DecimalField(decimal_places=2, max_digits=4)
    analysis_type = models.CharField(max_length=10, default='day')
    pie_type = models.CharField(max_length=40, choices=PIE_TYPE_CHOICES)

    class Meta:
        abstract = False
        db_table = u'Pie_Data_Distribution'
        verbose_name = '首页饼图数据'
        ordering = ['-analysis_time']


class RunStatisticsData(models.Model):
    dataA = models.IntegerField(default=0)
    dataB = models.IntegerField(default=0)
    dataC = models.IntegerField(default=0)
    dataD = models.IntegerField(default=0)

    class Meta:
        abstract = False
        db_table = u'running_statistics_data'
        verbose_name = '运行统计数据'
        ordering = ['-id']


