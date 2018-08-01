# coding=utf-8
from django.shortcuts import render
from cgmapp.models import Reading
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from datetime import timedelta
from twilio.rest import TwilioRestClient
import time
import telegram
import nightscout

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm #Para crear formularios (para login)
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

def alert_sms(username, date, valor, mingluc, maxgluc):
	message = "ALERTA DE GLUCOSA.\n" + "Usuario: " + str(username) +"\n" + "Fecha: " + str(date) + "\n" + "Valor: " + str(valor)
	client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
	if (valor < mingluc):
		message += " inferior al mínimo[" + mingluc + "]"
	elif (valor > maxgluc):
		message += " superior al maximo[" + maxgluc + "]"
	client.messages.create(body=message, to="+34637298394", from_="")


def alert_telegram(username, date, valor, mingluc, maxgluc):
	message = "ALERTA DE GLUCOSA.\n" + "Usuario: " + str(username) +"\n" + "Fecha: " + str(date) + "\n" + "Valor: " + str(valor)
	if (valor < mingluc):
		message += " inferior al mínimo[" + mingluc + "]"
	elif (valor > maxgluc):
		message += " superior al maximo[" + maxgluc + "]"
	bot = telegram.Bot(token='567375109:AAFQTI8N7kiLAFSQm5KEzmM0uWR4Xq8XW3o')
	bot.sendMessage(chat_id='-1001348736833', text=message)


def index(request):
	ming=70
	maxg=110
	#twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
	#twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/cgmapp/login')
	try:
		readings_list = Reading.objects.get(username=request.user).history_set.all()
	except:
		readings_list = ''
	if request.POST.has_key('read'):
		'''
		llamar api heroku
		timenow = datetime.now()
		time.sleep(10)	#10 segundos de margen para realizar la lectura
		heroku = herokuapi.HerokuAPI(api_key, api_secret, format)
		readget = heroku.get	
		valorhk = readget.

		guardar valor
		read = Reading(username=request.user, date=timenow, valor=valorhk)
		read.save()  		

		smscb = request.GET['smscb']
		telegramcb = request.GET['telegramcb']
		if smscb:
			alert_sms(username, date, valor, mingluc, maxgluc)
		if telegramcb:
			alert_telegram(username, date, valor, mingluc, maxgluc)
		'''
		pass
	elif request.POST.has_key('filter'):
		'''
		opt = request.GET.get('dropdown','alld')
		if opt == "alld":
			readings_list = Reading.objects.get(username=request.user).history_set.all()
			context = {'readings_list':readings_list}
			return render(request, 'cgmapp/index.html', context)
		if opt == "1d":
			td=1
		elif opt == "3d":
			td=3
		elif opt == "1w":
			td=7
		d=date.today()-timedelta(days=td)
		readings_list= Reading.objects.get(username=request.user).filter(date__gte=d)
		context = {'readings_list':readings_list}
		return render(request, 'cgmapp/index.html', context)
		'''
		pass	
	elif request.POST.has_key('delete'):
		for r in readings_list:
			r.delete()
		readings_list = Reading.objects.get(username=request.user).history_set.all()
		context = {'readings_list':readings_list}
		return render(request, 'cgmapp/index.html', context)
	elif request.POST.has_key('config'):
		errors=[]
		ming = request.POST['mingluc']
		maxg = request.POST['maxgluc']
		try:
			ming = int(ming)
			maxg = int(maxg)
			if(ming>maxg):
				errors.append('Max must be greater than min')
			else:
				context={'mingluc':ming, 'maxgluc':maxg}
				return render(request, 'cgmapp/index.html', context)
		except:
			errors.append('Inputs must be integers')
		if errors != []:
			ming=70
			maxg=110
		return render(request, 'cgmapp/index.html', {'errors':errors,'mingluc':ming,'maxgluc':maxg})
	context = {'user':request.user,'readings_list':readings_list,'mingluc':ming,'maxgluc':maxg}
	return render(request, 'cgmapp/index.html', context)


def config(request):
	errors=[]
	if not request.user.is_authenticated():
		return HttpResponseRedirect('cgmapp/login')
	answer=request.POST.get('test',10)
	if answer=="ab":
		return HttpResponseRedirect('/cgmapp')
	if request.method=='POST':	
		ming = request.POST['mingluc']
		maxg = request.POST['maxgluc']
		try:
			ming = int(ming)
			maxg = int(maxg)
			if(ming > maxg):
				errors.append('Max must be greater than min.')
			else:
				context={'mingluc':ming, 'maxgluc':maxg}
				return render(request, 'cgmapp/config.html', context)
		except:
			errors.append('Inputs must be integers.')			
	return render(request, 'cgmapp/config.html', {'errors':errors})


def show(request, read_id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('cgmapp/login')
	try:
		read = Reading.objects.get(id=read_id)
	except:
		pass
	context = {'user':request.user, 'read': read}
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
