# Generated by Django 2.0 on 2022-12-14 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0006_remove_question_optionsino'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='optionSiNo',
            field=models.BooleanField(default=False, help_text='Marca esta casilla para que las opciones sean Si o No. No podrás añadir más opciones'),
        ),
    ]
