from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login

def home(request):
	return HttpResponseRedirect('/lib/')

def login(request):
    data= {}
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
                if user.is_superuser:
                    return HttpResponseRedirect('/lib/librarian/')
                else:
                    return HttpResponseRedirect('/')
            else:
                # Account if disabled
                data['error_message'] = "Your account is disabled"
                return render(request, "login.html", data)
        else:
            # Invalid login
            data['error_message'] = "Invalid login"
            return render(request, "login.html", data)
    else:
        return render(request, "login.html", {})

@login_required(login_url='/login/')
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/login/')
def forgetpass(request):
    data = {}
    if request.method == 'POST':
        studentid = request.POST['studentid']
        email = request.POST['email']
        try:
            studentx = Student.objects.get(student_ID = studentid)
        except:
            data['error_message'] = 'Student ID Not Found'
            return render(request, "forgetp.html", {})
        if(studentx.user.email != email):
            data['error_message'] = 'Student ID and email isn\'t match'
            return render(request, "forgetp.html", {})
        else:
            passwd = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
            mail_message = 'Dear '+studentx.user.first_name+' '+studentx.user.last_name
            mail_message += '\n\n\n\t Your password is reset!!\n\t So your new password is: '+passwd
            mail_message += '\n\n\nThank, \nSmart-Library Teams.'
            send_mail(
                'Your Account\'s password is reset!',
                mail_message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=True,
            )
            studentx.user.set_password(passwd)
            studentx.user.save()
            return HttpResponseRedirect('/')
    return render(request, "forgetp.html", {})
