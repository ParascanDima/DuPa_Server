import urllib.request
import json

class Weather:
	"""docstring for Weather"""
	def __init__(self, city, temp, humidity, wind_speed, wind_dir):
		self.city = city
		self.temp = temp
		self.humidity = humidity
		self.wind_speed = wind_speed
		self.wind_dir = wind_dir

	def GetCity(self):
		return self.city

	def GetTemperature(self):
		return self.temp

	def GetHumidity(self):
		return self.humidity

	def GetWindSpeed(self):
		return self.wind_speed

	def GetWindDirection(self):
		return self.wind_dir


def GetWeatherJSON(city = 'Chisinau'):
	json_link = 'http://api.wunderground.com/api/e295a28efdb4d3fe/geolookup/conditions/q/RepublicOfMoldova/Chisinau.json'

	if city == 'Kiev':
		json_link = 'http://api.wunderground.com/api/e295a28efdb4d3fe/geolookup/conditions/q/Ucraine/Kiev.json'

	f = urllib.request.urlopen(json_link)
	json_string = "".join(map(chr, f.read())) 
	parsed_json = json.loads(json_string)
	weather_json = Weather(parsed_json['location']['city'], parsed_json['current_observation']['temp_c'], parsed_json['current_observation']['relative_humidity'],
		parsed_json['current_observation']['wind_kph'], parsed_json['current_observation']['wind_dir'])
	f.close()

	return weather_json

