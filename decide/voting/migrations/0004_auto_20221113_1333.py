# Generated by Django 2.0 on 2022-11-13 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0003_auto_20180605_0842'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voting',
            name='question',
        ),
        migrations.AddField(
            model_name='voting',
            name='question',
            field=models.ManyToManyField(related_name='votings', to='voting.Question'),
        ),
    ]
