from django.db import models
from django.contrib.auth.models import User as django_user

class Reading (models.Model):
	username = models.ForeignKey(django_user)
	valor = models.IntegerField()
	date = models.CharField(max_length=25)

	def __unicode__(self):
		return self.date
