import dateutil.parser
from datetime import datetime

class BaseModel(object):
	def __init__(self, **kwargs):
		self.param_defaults = {}

class SGV(BaseModel):
	def __init__(self, **kwargs):
		self.param_defaults = {
			'sgv': None,
			'dateString' : None,
		}

		for (param, default) in self.param_defaults.items():
			setattr(self, param, kwargs.get(param, default))

