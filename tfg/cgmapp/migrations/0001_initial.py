# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Reading',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('valor', models.IntegerField()),
                ('date', models.DateField()),
            ],
        ),
    ]
