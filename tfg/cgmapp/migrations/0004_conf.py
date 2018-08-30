# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cgmapp', '0003_auto_20180828_1042'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conf',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ming', models.IntegerField()),
                ('maxg', models.IntegerField()),
                ('smscheck', models.BooleanField(default=False)),
                ('tgcheck', models.BooleanField(default=False)),
                ('date', models.DateField()),
                ('username', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
