from django.conf.urls import include,patterns,url
from cgmapp import views

urlpatterns = patterns('', 
	url(r'^register/', views.register, name='register'),
	url(r'^login/', views.login, name='login'),#pantalla de login
	url(r'^', include('django.contrib.auth.urls')),
	url(r'^$', views.index, name='index'),
	)
