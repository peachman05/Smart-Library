from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def home(request):
	appname = "Smart Library"
	return render(request, 'home.html', {'appname': appname})