# Generated by Django 3.1.1 on 2020-09-23 20:39

import datetime
import django.core.validators
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('shortener', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='hash',
            field=models.CharField(default=None, max_length=20),
        ),
        migrations.AlterField(
            model_name='link',
            name='preferred_url',
            field=models.CharField(default=None, max_length=30),
        ),
        migrations.AlterField(
            model_name='link',
            name='url',
            field=models.CharField(max_length=1024, unique=True, validators=[django.core.validators.URLValidator]),
        ),
        migrations.AlterField(
            model_name='linkinfo',
            name='creation_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 23, 20, 39, 6, 91093, tzinfo=utc)),
        ),
    ]
