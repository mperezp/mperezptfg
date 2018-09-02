# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cgmapp', '0004_conf'),
    ]

    operations = [
        migrations.AddField(
            model_name='reading',
            name='is_alert',
            field=models.BooleanField(default=False),
        ),
    ]
