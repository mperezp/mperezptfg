import dateutil.parser
from datetime import datetime

class BaseModel(object):
	def __init__(self, **kwargs):
		self.param_defaults = {}

	@classmethod
	def json_transforms(cls, json_data):
		pass

	@classmethod
	def new_from_json_dict(cls, data, **kwargs):
		json_data = data.copy()
		if kwargs:
			for key, val in kwargs.items():
				json_data[key] = val

		cls.json_transforms(json_data)

		c = cls(**json_data)
		c._json = data
		return c


class SGV(BaseModel):
	def __init__(self, **kwargs):
		self.param_defaults = {
			'sgv': None,
			'date' : None,
		}

		for (param, default) in self.param_defaults.items():
			setattr(self, param, kwargs.get(param, default))

	@classmethod
	def json_transforms(cls, json_data):
		if json_data.get('dateString'):
			json_data['date'] = dateutil.parser.parse(json_data['dateString'])

