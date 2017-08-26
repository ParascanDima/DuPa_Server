# -*- coding: iso-8859-15 -*-

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from IrrigationSystem.weather import weatherlib
from IrrigationSystem.models import Wind, MeasureTime, GroundHumidity, Custom_User
from ipware.ip import get_ip
from ipaddress import ip_address
import datetime
import socket
import json

GSM_IP = None

def index(request):
    return render(request, 'IrrigationSystem/home.html', {"class_active" : "index"})


def contact(request):
    return render(request, 'IrrigationSystem/basic.html',
                  {'content': [u'Номер мобильного(Moldcell): 079-22-98-87', u'Номер мобильного(Orange): 068-04-72-77', u'Почта: parascan.dima94@gmail.com'], "class_active" : "contact"})

def blog(request):
	return render(request, 'IrrigationSystem/basic.html',
                  {'content': ['Here will be schema of teritory sequences'], "class_active" : "blog"})

def weather(request, city = "Chisinau"):
	global weather_json

	weather_json = weatherlib.GetWeatherJSON(city)

	return render(request, 'IrrigationSystem/weather.html', 
				  {'city' : weather_json.GetCity(),
				   'temperature': weather_json.GetTemperature(),
				   'humidity': weather_json.GetHumidity(),
				   'wind_speed': weather_json.GetWindSpeed(),
				   'wind_direction': weather_json.GetWindDirection(),})

def SocketSend(request, function):
	"""
	Functionality for sending 
	"""
	host = '192.168.82.196'
	port = 12345

	if function == "watering":
		message = b'Start watering'
		content = {'content': ['Полив начанётся в течении одной минуты']}
	elif function == "collectdata":
		message = b'Start collecting data'
		content = {'content': ['Сбор данных начанётся в течении одной минуты']}

	s = socket.socket()         # Create a socket object
	try:
		s.connect((host, port))
		s.sendall(message)
		s.close()
	except Exception as e:
		return render(request, 'IrrigationSystem/basic.html',
                  {'content': ['Ошибка подключения к системе полива']})

	return render(request, 'IrrigationSystem/basic.html', content)


def DataTransfer(request):
	invalid_key = "Invalid Key"
	success = "Success"
	failed  = "Failed"
	if request.method == 'POST':
		json_string = "".join(map(chr, request.body))
		json_data = json.loads(json_string)
		try:
			wind_speed = Wind(speed = json_data["Wind_speed"])
			humidity = GroundHumidity(sensor = json_data["humidity"], averange=json_data["humidity"])
			measure_time = MeasureTime(date = datetime.datetime.now())
			measure_time.save()
			wind_speed.date = measure_time
			humidity.date = measure_time
			wind_speed.save()
			humidity.save()
		except KeyError:
			return HttpResponse(invalid_key)

		except Exception:
			return HttpResponse(failed)

		return HttpResponse(success)
	else:
	    return HttpResponse("Is not POST method")
	

def WindSpeedChartRender(request):
	return render(request, 'IrrigationSystem/chart.html', {"endpoint": "windspeedchart", "legend_label": "скорость, м/с"})


def windspeedchart(request):
	wind_objects = list(Wind.objects.all().order_by('date__date'))
	data_set = [d.speed for d in wind_objects]
	labels = [d.date.date.strftime('%d-%m-%Y %H:%M:%S') for d in wind_objects]
	data = {
		'data_set': data_set,
		'labels': labels,
	}
	return JsonResponse(data)

def GroundHumidityChartRender(request):
	return render(request, 'IrrigationSystem/chart.html', {"endpoint": "groundhumiditychart", "legend_label": "влажность"})

def groundhumiditychart(request):
	grhum_objects = list(GroundHumidity.objects.all().order_by('date__date'))
	data_set = [d.sensor for d in grhum_objects]
	labels = [d.date.date.strftime('%d-%m-%Y %H:%M:%S') for d in grhum_objects]
	data = {
		'data_set': data_set,
		'labels': labels,
	}
	return JsonResponse(data)

def SaveIP(request):
	global GSM_IP
	ip = get_ip(request)
	if ip is not None:
		GSM_IP = ip
		return HttpResponse("Thanks, is OK")
	else:
		return HttpResponse("Oops, something wrong")
