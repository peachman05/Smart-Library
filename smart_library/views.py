from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

def home(request):
	appname = "Smart Library"
	return render(request, 'home.html', {'appname': appname})