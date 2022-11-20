from django.db import models


class Census(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()

    
    class Meta:
        unique_together = (('voting_id', 'voter_id'),)


class ExcelFile(models.Model):
    file = models.FileField(upload_to="excel")
    
    CSV = 'csv'
    XLSX = 'excel'

    FILE_TYPES = [
        (CSV, 'csv'), 
        (XLSX, 'excel')
    ]

    file_type = models.CharField(max_length=4,
    choices=  FILE_TYPES,
    default= XLSX)