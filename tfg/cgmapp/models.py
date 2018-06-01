from django.db import models
from django.contrib.auth.models import User as django_user

class Reading (models.Model):
	id = models.AutoField(primary_key=True)
	username = models.ForeignKey(django_user)
	valor = models.IntegerField()
	date = models.DateField()

	def __unicode__(self):
		return self.id
