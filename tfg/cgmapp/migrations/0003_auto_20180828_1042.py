# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cgmapp', '0002_reading_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reading',
            name='date',
            field=models.CharField(max_length=25),
        ),
        migrations.AlterField(
            model_name='reading',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
        ),
    ]
