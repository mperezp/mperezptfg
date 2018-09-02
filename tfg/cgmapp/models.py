from django.db import models
from django.contrib.auth.models import User as django_user

class Reading (models.Model):
	username = models.ForeignKey(django_user)
	valor = models.IntegerField()
	date = models.CharField(max_length=25)
	is_alert = models.BooleanField(default=False)

	def __unicode__(self):
		return self.date

class Conf (models.Model):
	username = models.ForeignKey(django_user)
	ming = models.IntegerField()
	maxg = models.IntegerField()
	smscheck = models.BooleanField(default=False)
	tgcheck = models.BooleanField(default=False)
	date = models.DateField()
	
	def __unicode__(self):
		return self.date
