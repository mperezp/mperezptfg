import requests
import hashlib
from models import SGV

class Api(object):

	def __init__(self, site_url):
		self.site_url = site_url

	def getCurrentSgv(self):
		r = requests.get(self.site_url + '/api/v1/entries/current.json')
		temp = r.json()
		valor = temp[0]['sgv']
		date = temp[0]['dateString']
		sgv = SGV(sgv=valor, dateString=date)
		return sgv
