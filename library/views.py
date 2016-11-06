from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student, BookCatagories, Book, Transaction
from django.contrib.auth.models import User
from django.db.models import Q
import string
import random
from django.core.mail import send_mail
from django.conf import settings
from .forms import bookImgFileForm
import datetime

BOOK_DUE_DATE = 8
BOOK_LIMIT = 5
FINE_RATE = 3

def home(request):
	return render(request, 'homepage.html', {})

@login_required
def profile(request):
	return render(request, 'homepage.html', {})



@login_required
def borrowBook(request):
	data = {}
	user = request.user
	student = Student.objects.get(user=user)
	book_list = Book.objects.all().filter(student = student)
	books = []
	book_amount = len(book_list)
	for book in book_list:
		book.borrow_date += datetime.timedelta(days=BOOK_DUE_DATE)
		books.append(book)
	data['book_list'] = books
	if request.method == 'POST':
		if 'submit_borrow' in request.POST:
			book_code = request.POST.get('search_book', False)
			book_borrow = Book.objects.get(code = book_code)
			if book_borrow.status == 'BW':
				data['error_message'] = 'Book is not available'
				return render(request, 'borrowbook.html', data)
			elif book_amount >= BOOK_LIMIT:
				data['error_message'] = 'You borrowed book limit is full!'
				return render(request, 'borrowbook.html', data)
			else:
				book_borrow.student = student
				book_borrow.status = 'BW'
				book_borrow.borrow_date = datetime.datetime.now()
				book_borrow.save()
				new_transaction = Transaction(date = datetime.datetime.now(), status='BR',
											  student = student, book=book_borrow)
				new_transaction.save()
		return HttpResponseRedirect("/lib/borrow/")
		# data['confirm_borrow']
	return render(request, 'borrowbook.html', data)



###################################### For Librarian ##################################
@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def backend_home(request):
	data = {'page': 'Dashboard'}
	data['user'] = request.user
	data['transactions'] = Transaction.objects.order_by('-date')[:30]	
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
			cata.delete()
		elif 'add_book' in request.POST:
			ab_name = request.POST.get('add_name', False)
			ab_author = request.POST.get('add_author', False)
			ab_code = request.POST.get('add_code', False)
			ab_date = request.POST.get('add_date', False)
			ab_isbn = request.POST.get('add_isbn', False)
			ab_address = request.POST.get('add_address', False)
			post_catagory = request.POST.get('ab_catagory', False)
			ab_catagory = BookCatagories.objects.get(name = post_catagory)
			ab_student = Student.objects.get(student_ID = 'libraryStore')
			try:
				upload_file = request.FILES['book_image']
			except:
				upload_file = False
			new_book = Book(name = ab_name, author = ab_author, address = ab_address,
							code = ab_code, date = ab_date, student = ab_student,
							isbn = ab_isbn, catagory = ab_catagory, picture=upload_file)
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
	data['form'] = bookImgFileForm()
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
				mail_message = 'Dear '+fname+' '+lname+'\n\n\n\t Your Account is all done!\n\t So your password is: '+passwd+'\n\n\nThank, \nSmart-Library Teams.'
				send_mail(
					'Your Registration is Successfull!',
					mail_message,
					settings.EMAIL_HOST_USER,
					[email],
					fail_silently=True,
				)
			except:
				user = User.objects.get(username=s_id)
				print('That user is exist')

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
					print('Can\'t find ' + student_selected[9:])
		return HttpResponseRedirect("/lib/librarian/backend_user/")
	#Ignore 'libraryStore'
	student_list = Student.objects.all().filter(~Q(student_ID = 'libraryStore'))
	quantity = []
	for student in student_list:
		quantity.append(len(Book.objects.all().filter(student = student)))
	data['student_list_q'] = [(i,j) for i,j in zip(student_list, quantity)]
	return render(request, 'backend_user.html', data)



@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def backend_setting(request):
	data = {'page': 'Setting'}
	data['user'] = request.user
	if request.method == 'POST':
		user = request.user
		if 'general' in request.POST:
			fname = request.POST.get('fname')
			lname = request.POST.get('lname')
			email = request.POST.get('email')
			user.first_name = fname
			user.last_name = lname
			user.email = email
			user.save()
		elif 'password-changed' in request.POST:
			oldpass = request.POST.get('old-pass')
			newpass1 = request.POST.get('new-pass1')
			newpass2 = request.POST.get('new-pass2')
			if user.check_password(oldpass) == True:
				if newpass1 == newpass2:
					user.set_password(newpass1)
					user.save()
					mail_message = 'Dear '+user.first_name+' '+user.last_name+'\n\n\n\t Your Account\'s Password is Changed. (Account: '+user.username+')\n\n\nThank, \nSmart-Library Teams.'
					send_mail(
						'Your Password Is Changed!',
						mail_message,
						settings.EMAIL_HOST_USER,
						[user.email],
						fail_silently=True,
					)
					return HttpResponseRedirect('/login/')
				else:
					data['error_message'] = 'New password isn\'t match'
					return render(request, 'backend_setting.html', data)
			else:
				data['error_message'] = 'Your old password is not correct'
				return render(request, 'backend_setting.html', data)
		return HttpResponseRedirect("/lib/librarian/backend_setting")
	return render(request, 'backend_setting.html', data)

@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def backend_returnbook(request):
	data = {'page': 'ReturnBook'}
	data['user'] = request.user
	if request.method == 'POST':
		if 'submit_search' in request.POST:
			search_student = request.POST.get('search_student')
			# try:
			student = Student.objects.get(student_ID = search_student)
			book_list = Book.objects.all().filter(student = student)
			books = []
			price = []
			data['student'] = student
			for book in book_list:
				book.borrow_date += datetime.timedelta(days=BOOK_DUE_DATE)
				books.append(book)
				over = datetime.datetime.now().date()-book.borrow_date.date()
				if(over.days > 0):
					price.append(over.days*FINE_RATE)
				else:
					price.append(0)
			data['book_list'] = zip(books, price)
			return render(request, 'backend_returnBook.html', data)
		elif 'return_book' in request.POST:
			student_return = request.POST.get('student_return')
			for book_selected in request.POST.getlist('bookTable'):
				b = Book.objects.get(code = (book_selected[9:]))
				b.status = 'AL'
				store = Student.objects.get(student_ID = 'libraryStore')
				b.student = store
				b.save()
				student = Student.objects.get(student_ID = student_return)
				new_transaction = Transaction(date = datetime.datetime.now(), status='RT',
											  student = student, book=b)
				new_transaction.save()
		return HttpResponseRedirect("/lib/librarian/backend_returnbook/")
	return render(request, 'backend_returnBook.html', data)
