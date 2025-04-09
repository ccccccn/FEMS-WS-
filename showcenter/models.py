from django.db import models


# Create your models here.

class PieDistribution(models.Model):
    PIE_TYPE_CHOICES = [
        ('Soc_distribution', 'Soc distribution'),
        ('Frequency_Distribution', 'Frequency Distribution'),
        ('Duration_distribution', 'Duration Distribution')
    ]
    analysis_time = models.DateTimeField(auto_now_add=True)
    partition1 = models.FloatField()
    partition2 = models.FloatField()
    partition3 = models.FloatField()
    partition4 = models.FloatField()
    partition5 = models.FloatField()
    analysis_type = models.CharField(max_length=10, default='day')
    pie_type = models.CharField(max_length=40,choices=PIE_TYPE_CHOICES)
    class Meta:
        db_table = u'Pie_Data_Distribution'

