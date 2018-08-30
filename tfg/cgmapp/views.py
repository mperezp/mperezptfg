# coding=utf-8
from django.shortcuts import render
from cgmapp.models import Reading, Conf
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from datetime import timedelta, datetime
from twilio.rest import Client
import time
import telegram
import nightscout
import json

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm #Para crear formularios (para login)
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

def alert_sms(username, date, valor, mingluc, maxgluc):
	message = "ALERTA DE GLUCOSA.\n" + "Usuario: " + str(username) +"\n" + "Fecha: " + str(date) + "\n" + "Valor: " + str(valor)
	client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
	if (valor < mingluc):
		message += " inferior al mínimo[" + str(mingluc) + "]"
	elif (valor > maxgluc):
		message += " superior al maximo[" + str(maxgluc) + "]"
	client.messages.create(body=message, to="+34637298394", from_="+34911062133")


def alert_telegram(username, date, valor, mingluc, maxgluc):
	bottoken='567375109:AAFQTI8N7kiLAFSQm5KEzmM0uWR4Xq8XW3o'
	chatId='-1001348736833'
	message = "ALERTA DE GLUCOSA.\n" + "Usuario: " + str(username) +"\n" + "Fecha: " + str(date) + "\n" + "Valor: " + str(valor)
	if (valor < mingluc):
		message += " inferior al mínimo[" + str(mingluc) + "]"
	elif (valor > maxgluc):
		message += " superior al maximo[" + str(maxgluc) + "]"
	bot = telegram.Bot(token=bottoken)	#obtenemos el bot creado
	bot.sendMessage(chat_id=chatId, text=message)		#enviamos el mensaje al chat indicado


def index(request):
	ming=None	#mínimo estándar en ayunas
	maxg=None	#máximo estándar en ayunas
	tend=None	#tendencia de los niveles de glucosa (comparacion actual con previa)
	last_read=None	#valor de la última lectura registrada en el sistema
	read=None
	api = nightscout.Api('https://mperezpcgm.herokuapp.com')	#nuestra api de nightscout
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/cgmapp/login')	#si no esta logeado, tiene que hacerlo
	readings_list = User.objects.get(username=request.user).reading_set.all()	#obtenemos el histórico del usuario
	try:
		conf = User.objects.get(username=request.user).conf_set.last()
		conf.save()
	except:
		conf = Conf(username=request.user, ming=70, maxg=110, smscheck=False, tgcheck=False, date=datetime.now())
		conf.save()
	if request.POST.has_key('read'):	#si queremos realizar una lectura
		currentsgv = api.getCurrentSgv()		#obtenemos el SGV (Sensor Glucose Value) actual
		valorc = int(currentsgv.sgv)			#tomamos el campo valor del SGV
		datec = currentsgv.dateString		#tomamos el campo fecha del sgv
		if readings_list:	#si hay lecturas en la lista
			for r in readings_list:		#recorremos la lista de lecturas del usuario
				if r.date == datec:		#si la fecha de la lectura ya está en la lista, la lectura falló
					context = {'readings_list': readings_list, 'mingluc':ming, 'maxgluc':maxg, 'read_error':'yes'}	#mostramos un mensaje de error al usuario
					return render(request, 'cgmapp/index.html', context)
		try:
			last_read = readings_list.last()
		except:
			pass
		read = Reading(username=request.user, date=datec, valor=valorc)	#creamos una nueva entrada en el historial del usuario
		read.save()  	#guardamos los cambios
		try:	#comprobamos si ya hay algún valor almacenado para comprobar la tendencia
			if read.valor < last_read.valor:
				tend = 'desc'
			elif read.valor > last_read.valor:
				tend = 'asc'
			else:
				tend = 'norm'
		except:
			pass
		if (read.valor < ming or read.valor > maxg):	#si se detecta que la lectura es anormal, se llama a los servicios externos
			smscb = conf.smscheck	#estado de la opción de SMS
			telegramcb = conf.tgcheck
			if smscb:
				alert_sms(request.user, read.date, read.valor, conf.ming, conf.maxg)	#si está marcada la opción de alerta por sms, invocamos al servicio

			if telegramcb:
				alert_telegram(request.user, read.date, read.valor, conf.ming, conf.maxg)	#si está marcada la opción de telegram, invocamos al servicio
	elif request.POST.has_key('filter'):
		day = request.POST['datefilt']
		y,m,d = day.split("-")
		filt = d + "-" + m + "-" + y
		readings_list= User.objects.get(username=request.user).reading_set.filter(date__gte=filt)
		context = {'readings_list':readings_list,'mingluc':conf.ming, 'maxgluc':conf.maxg}
		return render(request, 'cgmapp/index.html', context)	
	elif request.POST.has_key('delete'):
		for r in readings_list:		#para cada lectura almacenada del usuario
			r.delete()		#la borramos
		readings_list = User.objects.get(username=request.user).reading_set.all()	#y obtenemos una nueva lista vacía
		context = {'readings_list':readings_list,'mingluc':conf.ming, 'maxgluc':conf.maxg}
		return render(request, 'cgmapp/index.html', context)
	elif request.POST.has_key('config'):
		errors=[]
		mingl = request.POST['mingluc']
		maxgl = request.POST['maxgluc']
		sms = request.POST.get('smscb', False)
		telegram = request.POST.get('telegramcb', False) 
		try:
			mingl = int(mingl)								#miramos si los parámetros son enteros
			maxgl = int(maxgl)
			if(mingl>maxgl):									#y si el mínimo es superior al máximo
				errors.append('El máximo debe ser superior al mínimo')
			else:											#si entramos aquí, los datos introducidos son correctos
				if sms=="on":
					sms=True
				if telegram=="on":
					telegram=True
				conf = Conf(username=request.user, ming=mingl, maxg=maxgl, smscheck=sms, tgcheck=telegram, date=datetime.now())
				conf.save()
				context={'readings_list':readings_list,'mingluc':conf.ming, 'maxgluc':conf.maxg, 'smscb':conf.smscheck, 'telegramcb':conf.tgcheck}
				return render(request, 'cgmapp/index.html', context)
		except:
			errors.append('Los valores deben ser enteros')
		if errors != []:		#si hay algún error, obtenemos la última configuración válida
			conf = User.objects.get(username=request.user).conf_set.last()
		return render(request, 'cgmapp/index.html', {'readings_list':readings_list,'errors':errors,'mingluc':conf.ming,'maxgluc':conf.maxg, 'smscb':conf.smscheck, 'telegramcb':conf.tgcheck})
	context = {'user':request.user,'readings_list':readings_list,'mingluc':conf.ming,'maxgluc':conf.maxg, 'tend':tend, 'read':read, 'smscb':conf.smscheck, 'telegramcb':conf.tgcheck}
	return render(request, 'cgmapp/index.html', context)


def config(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('cgmapp/login')
	context={}
	return render(request, 'cgmapp/config.html', context)


def show(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('cgmapp/login')
	readings_list = User.objects.get(username=request.user).reading_set.all()
	context = {'user':request.user, 'readings_list': readings_list}
	return render(request, 'cgmapp/show.html', context)


def login(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect("/cgmapp/") #si esta logeado, lo enviamos a la pantalla principal
	if request.method == 'POST':
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			user = request.POST['username'] #cogemos usuario y pass
			password = request.POST['password']
			access = authenticate(username=user, password=password) #autenticamos y guardamos la respuesta en access
			if access is not None: #si ha ido bien, logeamos al usuario en django
				auth_login(request, access)
				return HttpResponseRedirect("/cgmapp") #redireccionamos a la vista principal
	else:
		form = AuthenticationForm()
	return render(request, 'cgmapp/registration/login.html', {'form': form})


def register(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			new_user = form.save()
			user = request.POST['username']
			password = request.POST['password1']
			access = authenticate(username=user, password=password)
			if access is not None:
				auth_login(request, access)
				return HttpResponseRedirect("/cgmapp")
	else:
		form = UserCreationForm()
	return render(request, "cgmapp/registration/register.html", {
		'form': form
	})
