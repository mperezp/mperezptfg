from django.shortcuts import render
from cgmapp.models import Reading
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm #Para crear formularios (para login)
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

def index(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('cgmapp/login')
	try:
		readings_list = Reading.objects.get(username=request.user).history_set.all()
	except:
		readings_list = ''
	if request.POST.has_key('delete'):
		for r in readings_list:
			r.delete()
		readings_list = Reading.objects.get(username=request.user).history_set.all()
		context = {'readings_list':readings_list}
		return render(request, 'cgmapp/index.html', context)
	context = {'user':request.user,'readings_list':readings_list}
	return render(request, 'cgmapp/index.html', context)

def config(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('cgmapp/login')
	context = {'min':70, 'max':110}
	return render(request, 'cgmapp/config.html', context)

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
