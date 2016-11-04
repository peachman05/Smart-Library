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
	if request.method == 'POST':
		if 'book_search' in request.POST:
			s_status = request.POST.get('status', False)
			s_catagory = request.POST.get('catagory_name', False)
			book_list = Book.objects.all()
			if s_status != 'all':
				book_list = book_list.filter(status = s_status)
			if s_catagory != 'all':
				cata = BookCatagories.objects.get(name = s_catagory)
				book_list = book_list.filter(catagory = cata)
			data['book_list'] = book_list
			data['catagories_list'] = BookCatagories.objects.all()
			return render(request, 'backend_addbook.html', data)
		elif 'add_catagory' in request.POST:
			cata_name = request.POST.get('catagory_name')
			try:
				BookCatagories.objects.get(name = cata_name)
			except:
				cata = BookCatagories(name = cata_name)
				cata.save()
		elif 'delete_catagory' in request.POST:
			cata_name = request.POST.get('catagory_name')
			cata = BookCatagories.objects.get(name = cata_name)
			books = Book.objects.all().filter(catagory = cata)
			for book in books:
				book.delete()
			cata.delete
		elif 'add_book' in request.POST:
			ab_name = request.POST.get('add_name', False)
			ab_author = request.POST.get('add_author', False)
			ab_code = request.POST.get('add_code', False)
			ab_date = request.POST.get('add_date', False)
			ab_isbn = request.POST.get('add_isbn', False)
			post_catagory = request.POST.get('ab_catagory', False)
			ab_catagory = BookCatagories.objects.get(name = post_catagory)
			ab_student = Student.objects.get(student_ID = 'libraryStore')
			new_book = Book(name = ab_name, author = ab_author,
							code = ab_code, date = ab_date, student = ab_student,
							isbn = ab_isbn, catagory = ab_catagory)
			new_book.save()
		elif 'delete_book' in request.POST:
			for book_selected in request.POST.getlist('bookTable'):
				try:
					b = Book.objects.get(pk = book_selected[9:])
					b.delete()
				except:
					print("Can't Delete Book")
		return HttpResponseRedirect("/lib/librarian/backend_addbook/")
	data['book_list'] = Book.objects.all()
	data['catagories_list'] = BookCatagories.objects.all()
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
		elif 'delete_user' in request.POST:
			for student_selected in request.POST.getlist('studentTable'):
				try:
					u = User.objects.get(username = (student_selected[9:]))
					s = Student.objects.get(user = u)
					u.delete()
					s.delete()
				except :
					print('Can\'t find ' + student_selected[9:]	)
		return HttpResponseRedirect("/lib/librarian/backend_user/")
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