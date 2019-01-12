# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from IrrigationSystem.weather import weatherlib
from IrrigationSystem.models import Wind, MeasureTime, GroundHumidity, Custom_User
from ipware.ip import get_ip
from django.views.decorators.csrf import csrf_exempt
import datetime
import os
import socket
import json
import threading

subscribers = []
timeViewThread = None


def StartFuntion():
	global gsmConnectionEntity
	activeConnection = gsmConnectionEntity.GetActiveConnection()
	if gsmConnectionEntity._isConnected:
		activeConnection.sendall(b'Start watering\1\r\1\n')

def EndFuntion():
	global gsmConnectionEntity
	activeConnection = gsmConnectionEntity.GetActiveConnection()
	if gsmConnectionEntity._isConnected:
		activeConnection.sendall(b'Stop watering\1\r\1\n')

def CheckTime(startTime=None, endTime=None, startFunc=None, endFunc=None):
	while True:
		if startTime < datetime.datetime.now():
			break
	startFunc()

	while True:
		if endTime < datetime.datetime.now():
			break
	endFunc()
	
def TCP_Listner(connectionEntity):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	try:
		s.bind(('', connectionEntity.port))
	except:
		connectionEntity._activeConnection.shutdown(socket.SHUT_RD)
	s.listen(1)
	connectionEntity._activeConnection, (connectionEntity._ip_addr, wtf) = s.accept()

	connectionEntity._activeConnection.settimeout(60.0)
	connectionEntity._isConnected = True
	connectionEntity.checkConnectionThread = threading.Thread(target=gsmConnectionEntity.CheckConnection)
	connectionEntity.checkConnectionThread.daemon = True
	connectionEntity.checkConnectionThread.start()
	connectionEntity.listnerThread = None

class GsmCommand(object):

	def __init__(self):
		self.isWateringStarted = False
		self.isCollectingStarted = False
		self.commandSendTime = datetime.datetime.now()
		self.isActiveRequest = False

class GsmConnection(object):
	def __init__(self, port):
		self.port = port
		self._activeConnection = None
		self._ip_addr = None
		self._isConnected = False
		self.checkConnectionThread = None
		self.listnerThread = None
		self.commandStatus = GsmCommand()

	def GetActiveConnection(self):
		return self._activeConnection

	def CheckConnection(self):

		while True:
			if self._activeConnection is not None:
				try:
					data = self._activeConnection.recv(1024)
					if not data:
						pass
					elif "Collecting started" in data.decode("utf-8"):
						print("Collecting started")
						self.commandStatus.isCollectingStarted = True
						self.commandStatus.isActiveRequest = False
					elif "Watering started" in data.decode("utf-8"):
						print("Watering started")
						self.commandStatus.isWateringStarted = True
						self.commandStatus.isActiveRequest = False
					elif "Watering stopped" in data.decode("utf-8"):
						print("Watering stopped")
						self.commandStatus.isWateringStarted = False
						self.commandStatus.isActiveRequest = False
					else:
						print("WTF is going on?!")
				except:
					if self.commandStatus.isActiveRequest:
						self.CloseActiveConnection()
						self.commandStatus.isCollectingStarted = self.commandStatus.isWateringStarted = False
						self.commandStatus.isActiveRequest = False
			else:
				self.CloseActiveConnection()
				self.commandStatus.isCollectingStarted = self.commandStatus.isWateringStarted = False
				self.commandStatus.isActiveRequest = False
				break

	def StartListnerThread(self):
		self.listnerThread = threading.Thread(target=TCP_Listner, args={self})
		self.listnerThread.daemon = True
		self.listnerThread.start()


	def StopListnerThread(self):
		self.listnerThread.stop()

	def CloseActiveConnection(self):
		self._activeConnection = None
		self._isConnected = False
		self._ip_addr = None
		self.checkConnectionThread = None

gsmConnectionEntity = GsmConnection(351)

def index(request):
    return render(request, 'IrrigationSystem/home.html', {"class_active" : "index"})


def contact(request):
    return render(request, 'IrrigationSystem/basic.html',
                  {'content': [r'Номер мобильного(Moldcell): 079-22-98-87', r'Номер мобильного(Orange): 068-04-72-77', u'Почта: parascan.dima94@gmail.com'], "class_active" : "contact"})

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

def PlaneAction(request, function):
    return render(request, 'IrrigationSystem/planingTime.html', {"class_active" : "index"})

def SocketSend(request, function):
	"""
	Functionality for sending
	"""
	global gsmConnectionEntity
	try:
		activeConnection = gsmConnectionEntity.GetActiveConnection()
		if "sendstop" in request.path:
			if function == "watering":
				if gsmConnectionEntity.commandStatus.isWateringStarted is not False:
					message = b'Stop watering\1\r\1\n'
					content = {'content': [u'Полив будет отключён в течении одной минуты']}
				else:
					message = u''
					content = {'content': [u'Полив уже отключен']}
		else:
			if function == "watering":
				if gsmConnectionEntity.commandStatus.isWateringStarted is False:
					message = b'Start watering\1\r\1\n'
					content = {'content': [u'Полив начанётся в течении одной минуты']}
				else:
					message = u''
					content = {'content': [u'Полив уже включен']}

			elif function == "collectdata":
				if gsmConnectionEntity.commandStatus.isCollectingStarted is False:
					message = b'Start collecting data\1\r\1\n'
					content = {'content': [u'Сбор данных начанётся в течении одной минуты']}
				else:
					message = u''
					content = {'content': [u'Команда на сбор данных уже была отправлена, дождитесь ответа после чего можете попробовать ещё раз']}


	except Exception:
		return render(request, 'IrrigationSystem/basic.html', {'content': [u'Ошибка подключения к системе полива']})


	try:
		if gsmConnectionEntity._isConnected:
			if message != '':
				status = activeConnection.sendall(message)
				if not status:
					gsmConnectionEntity.commandStatus.isActiveRequest = True
					gsmConnectionEntity.commandStatus.commandSendTime = datetime.datetime.now()
			else:
				pass
		else:
			content = {'content': [u'GSM is not connected']}
	except:
		content = {'content': [u'Error occures while sending the message']}


	return render(request, 'IrrigationSystem/basic.html', content)


@csrf_exempt
def DataTransfer(request):
	invalid_key = "Invalid Key"
	success = "Success"
	failed  = "Failed"
	if request.method == 'POST':
		json_string = "".join(map(chr, request.body))
		json_data = json.loads(json_string)
		try:
			wind_speed = Wind(speed = json_data["Wind_speed"])
			humidity = GroundHumidity(sensor = json_data["Humidity"], averange=json_data["Humidity"])
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


@csrf_exempt
def PlanedTime(request):
	global timeViewThread
	success = "Success"
	failed  = "Failed"
	if request.method == 'POST':
		json_string = "".join(map(chr, request.body))
		json_data = json.loads(json_string)
		planedStart = datetime.datetime.strptime(json_data["start_time"], "%d %B %Y %H:%M:%S")
		planedStop = datetime.datetime.strptime(json_data["end_time"], "%d %B %Y %H:%M:%S")
		timeViewThread = threading.Thread(target=CheckTime, kwargs={"startTime":planedStart, "endTime":planedStop, "startFunc":StartFuntion, "endFunc":EndFuntion})
		timeViewThread.daemon = True
		timeViewThread.start()

	return render(request, 'IrrigationSystem/basic.html', {'content': [u'Полив начнётся в заданное время']})


def WindSpeedChartRender(request):
	return render(request, 'IrrigationSystem/chart.html', {"endpoint": "windspeedchart", "legend_label": u"скорость, м/с"})


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
	return render(request, 'IrrigationSystem/chart.html', {"endpoint": "groundhumiditychart", "legend_label": u"влажность"})

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
	global gsmConnectionEntity
	global subscribers

	ip = get_ip(request)
	if ip is not None:
		if gsmConnectionEntity.listnerThread is None:
			subscribers.append(ip)
			gsmConnectionEntity.StartListnerThread()

		return HttpResponse("Thanks, is OK")
	else:
		return HttpResponse("Oops, something wrong")

def ShowGSMIP(request):
	global gsmConnectionEntity

	if gsmConnectionEntity._ip_addr is not None:
		content = {'content':[gsmConnectionEntity._ip_addr]}
	else:
		content = {'content':[r'No connection']}

	return render(request, 'IrrigationSystem/basic.html', content)

