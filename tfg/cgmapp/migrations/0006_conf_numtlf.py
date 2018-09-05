# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cgmapp', '0005_reading_is_alert'),
    ]

    operations = [
        migrations.AddField(
            model_name='conf',
            name='numtlf',
            field=models.CharField(default=b'637298394', max_length=9),
        ),
    ]
