from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login

def home(request):
	return HttpResponseRedirect('/lib/')

def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/lib/')
    context = RequestContext(request)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth_login(request, user)
                # Done!
                return HttpResponseRedirect('/')
            else:
                # Account if disabled
                return HttpResponse('Your account is disabled')
        else:
            # Invalid login
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse('Invalid login' )
    else:
        return render(request, "login.html", {})

@login_required(login_url='/login/')
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/login/')