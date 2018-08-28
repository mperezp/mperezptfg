# coding=utf-8
from django.shortcuts import render
from cgmapp.models import Reading
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
	client.messages.create(body=message, to="+34637298394", from_="")


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
	ming=70	#mínimo estándar en ayunas
	maxg=110	#máximo estándar en ayunas
	tend=None	#tendencia de los niveles de glucosa (comparacion actual con previa)
	last_read=None	#valor de la última lectura registrada en el sistema
	api = nightscout.Api('https://mperezpcgm.herokuapp.com')	#nuestra api de nightscout
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/cgmapp/login')	#si no esta logeado, tiene que hacerlo
	readings_list = User.objects.get(username=request.user).reading_set.all()	#obtenemos el histórico del usuario
	try:
		last_read = readings_list.last()
	except:
		pass
	if request.POST.has_key('read'):	#si queremos realizar una lectura
		currentsgv = api.getCurrentSgv()		#obtenemos el SGV (Sensor Glucose Value) actual
		valorc = int(currentsgv.sgv)			#tomamos el campo valor del SGV
		datec = currentsgv.dateString		#tomamos el campo fecha del sgv
		if readings_list:	#si hay lecturas en la lista
			for r in readings_list:		#recorremos la lista de lecturas del usuario
				if r.date == datec:		#si la fecha de la lectura ya está en la lista, la lectura falló
					context = {'readings_list': readings_list, 'read_error':'yes'}	#mostramos un mensaje de error al usuario
					return render(request, 'cgmapp/index.html', context)
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
			smscb = request.GET.get('smscb',False)	#estado de la opción de SMS
			telegramcb = request.GET.get('telegramcb',False)	#estado de la opción de Telegram
			'''
			if smscb:
				alert_sms(request.user, read.date, read.valor, ming, maxg)	#si está marcada la opción de alerta por sms, invocamos al servicio
			'''
			if telegramcb:
				alert_telegram(request.user, read.date, read.valor, ming, maxg)	#si está marcada la opción de telegram, invocamos al servicio
		context= {'readings_list':readings_list, 'last_read':read, 'tend':tend, 'mingluc':ming,'maxgluc':maxg}
		return render(request, 'cgmapp/index.html', context)
	elif request.POST.has_key('filter'):
		opt = request.GET.get('dropdown','alld')
		if opt == "alld":
			readings_list = User.objects.get(username=request.user).reading_set.all()
			context = {'readings_list':readings_list}
			return render(request, 'cgmapp/index.html', context)
		if opt == "1d":
			td=1
		elif opt == "3d":
			td=3
		elif opt == "1s":
			td=7
		d=datetime.today()-timedelta(days=td)
		d=d.strftime("%d-%m-%Y %H:%M")
		readings_list= User.objects.get(username=request.user).reading_set.filter(date__gte=d)
		context = {'readings_list':readings_list,'mingluc':ming, 'maxgluc':maxg}
		return render(request, 'cgmapp/index.html', context)	
	elif request.POST.has_key('delete'):
		for r in readings_list:		#para cada lectura almacenada del usuario
			r.delete()		#la borramos
		readings_list = User.objects.get(username=request.user).reading_set.all()	#y obtenemos una nueva lista vacía
		context = {'readings_list':readings_list,'mingluc':ming, 'maxgluc':maxg}
		return render(request, 'cgmapp/index.html', context)
	elif request.POST.has_key('config'):
		errors=[]
		ming = request.POST['mingluc']
		maxg = request.POST['maxgluc']
		try:
			ming = int(ming)								#miramos si los parámetros son enteros
			maxg = int(maxg)
			if(ming>maxg):									#y si el mínimo es superior al máximo
				errors.append('El máximo debe ser superior al mínimo')
			else:											#si entramos aquí, los datos introducidos son correctos
				context={'readings_list':readings_list,'mingluc':ming, 'maxgluc':maxg}
				return render(request, 'cgmapp/index.html', context)
		except:
			errors.append('Los valores deben ser enteros')
		if errors != []:		#si hay algún error, ponemos el min y el max en los valores por defecto
			ming=70
			maxg=110
		return render(request, 'cgmapp/index.html', {'readings_list':readings_list,'errors':errors,'mingluc':ming,'maxgluc':maxg})
	context = {'user':request.user,'readings_list':readings_list,'mingluc':ming,'maxgluc':maxg, 'tend':tend, 'last_read':last_read}
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
