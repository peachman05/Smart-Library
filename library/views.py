from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student, BookCatagories, Book, Transaction
from django.contrib.auth.models import User
import string
import random

def home(request):
	return render(request, 'homepage.html', {})

def profile(request):
	return render(request, 'homepage.html', {})


@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def backend_home(request):
	data = {'page': 'Dashboard'}
	data['user'] = request.user
	return render(request, 'backend_home.html', data)

@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def backend_addbook(request):
	data = {'page': 'BookManager'}
	data['user'] = request.user
	return render(request, 'backend_addbook.html', data)


@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def backend_user(request):
	data = {'page': 'UserManager'}
	data['user'] = request.user
	if request.method == 'POST':
		if 'add_user' in request.POST:
			s_id = request.POST.get('student_ID', False)
			fname = request.POST.get('firstname', False)
			lname = request.POST.get('lastname', False)
			email = request.POST.get('email', False)
			passwd = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
			try:
				user = User.objects.create_user(s_id, email, passwd)
				user.first_name = fname
				user.last_name = lname
				user.save()
			except:
				user = User.objects.get(username=s_id)

			student = Student(student_ID = s_id, user=user)
			student.save()
			print(':   :  ' + s_id + ":" + fname + ":" + lname + ":" + email + " Password : " + passwd)
		else:
			for student_selected in request.POST.getlist('studentTable'):
				try:
					u = User.objects.get(username = (student_selected[9:]))
					s = Student.objects.get(user = u)
					u.delete()
					s.delete()
				except :
					print('Can\'t find ' + student_selected[9:]	)
	student_list = Student.objects.all()
	quantity = []
	for student in student_list:
		quantity.append(len(Book.objects.all().filter(student = student)))
	data['student_list_q'] = [(i,j) for i,j in zip(student_list, quantity)]
	return render(request, 'backend_user.html', data)



@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def backend_setting(request):
	data = {'page': 'Setting'}
	data['user'] = request.user

	return render(request, 'backend_setting.html', data)