# Generated by Django 2.0 on 2022-12-04 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0007_auto_20221204_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='optionSiNo',
            field=models.BooleanField(default=False, help_text='Marca esta casilla para que las opciones sean Si o No. No podrás añadir más opciones'),
        ),
    ]
