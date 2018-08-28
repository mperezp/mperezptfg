import requests
import dateutil.parser
from datetime import timedelta
from models import SGV

class Api(object):

	def __init__(self, site_url):
		self.site_url = site_url

	def getCurrentSgv(self):
		r = requests.get(self.site_url + '/api/v1/entries/current.json')
		temp = r.json()
		valor = temp[0]['sgv']
		date = temp[0]['dateString']
		parsed_date = dateutil.parser.parse(date)
		parsed_date = parsed_date + timedelta(hours=2)
		d = parsed_date.strftime("%d-%m-%Y %H:%M")
		sgv = SGV(sgv=valor, dateString=d)
		return sgv
