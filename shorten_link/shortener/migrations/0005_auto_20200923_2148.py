# Generated by Django 3.1.1 on 2020-09-23 21:48

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('shortener', '0004_auto_20200923_2052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='preferred_url',
            field=models.CharField(default='', max_length=60),
        ),
        migrations.AlterField(
            model_name='linkinfo',
            name='creation_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 23, 21, 48, 43, 980643, tzinfo=utc)),
        ),
    ]
