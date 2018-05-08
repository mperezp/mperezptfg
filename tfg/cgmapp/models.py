from django.db import models

class Reading (models.Model):
	id = models.AutoField(primary_key=True)
	valor = models.IntegerField()
	date = models.DateField()

	def __unicode__(self):
		return self.id
