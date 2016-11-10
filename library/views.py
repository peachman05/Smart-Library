from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student, BookCategories, Book, Transaction
from django.contrib.auth.models import User
from django.db.models import Q
import string
import random
import operator
from django.core.mail import send_mail
from django.conf import settings
from .forms import bookImgFileForm
from datetime import datetime, timedelta

BOOK_DUE_DATE = 5
BOOK_LIMIT = 5
FINE_RATE = 3

def home(request):


	cataAll = BookCategories.objects.all()
	cataCountDict = {} # key is category name
	for cataObj in cataAll:
		cataCountDict[cataObj.name] = Transaction.categoryCount(cataObj.name) #Transaction.objects.filter(book__category__name = cataObj.name ).count


	cataCountDict_Sort = sorted(cataCountDict.items(), key=operator.itemgetter(1) ,reverse=True)
	data = {}
	listShow = []
	for index in range(len(cataCountDict_Sort)) : #[i][0]->key ,[i][1] ->value(count)
		if cataCountDict_Sort[index][0] !='DeleteCat': # ignore 'DeleteCat' category
			bookArr = Book.objects.filter(category__name = cataCountDict_Sort[index][0]) # find bookAll from category
			temp = {}
			for bookObj in bookArr:
				countValue = Transaction.booknameCount(bookObj.name)
				if countValue > 0:
					temp[bookObj.name] = (countValue,bookObj)

			temp_sort = list(temp.items()) # output: [('BookName',(countValue,BookObj) ),(...)]
			temp_sort.sort(key=lambda x:x[1][0],reverse=True)
			# data['catName'+str(index+1)] = cataCountDict_Sort[index][0]
			# data['catValue'+str(index+1)] = temp_sort
			tempTuple = ( cataCountDict_Sort[index][0] ,temp_sort)
			if len(temp) > 0:
				listShow.append( tempTuple ) #output:[('CategoryName', temp_sort),(...)]



	data['user'] = request.user
	data['listShow'] = listShow
	data['test'] = datetime.now() - timedelta(days=30)
	return render(request, 'homepage.html', data )

@login_required(login_url='/login/')
def setting(request):
	data = {'user': request.user}
	user = request.user
	if user.is_superuser:
		return HttpResponseRedirect("/lib/")
	student = Student.objects.get(user = request.user)
	data['student'] = student
	if request.method == 'POST':
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
					student.setNewPassword(newpass1)
					return HttpResponseRedirect('/login/')
				else:
					data['error_message'] = 'New password isn\'t match'
					return render(request, 'setting.html', data)
			else:
				data['error_message'] = 'Your old password is not correct'
				return render(request, 'setting.html', data)
		return HttpResponseRedirect("/lib/setting/")
	return render(request, 'setting.html', data)


@login_required(login_url='/login/')
def borrowBookByCode(request, book_code):
	data = {}
	user = request.user
	if user.is_superuser:
		return HttpResponseRedirect("/lib/")
	student = Student.objects.get(user=user)
	data['student'] = student
	book_list = Book.objects.all().filter(student = student)
	books = []
	book_amount = len(book_list)
	for book in book_list:
		book.borrow_date += timedelta(days=BOOK_DUE_DATE)
		books.append(book)
	data['book_list'] = books	
	data['book_code'] = book_code
	return render(request, 'borrowbook.html', data)


@login_required(login_url='/login/')
def borrowBook(request):
	data = {}
	user = request.user
	if user.is_superuser:
		return HttpResponseRedirect("/lib/")
	student = Student.objects.get(user=user)
	data['student'] = student
	book_list = Book.objects.all().filter(student = student)
	books = []
	book_amount = len(book_list)
	for book in book_list:
		book.borrow_date += timedelta(days=BOOK_DUE_DATE)
		books.append(book)
	data['book_list'] = books
	if request.method == 'POST':
		if 'submit_borrow' in request.POST:
			book_code = request.POST.get('search_book', False)
			try:
				book_borrow = Book.objects.get(code = book_code)
			except:
				data['error_message'] = 'Book Not Found!'
				return render(request, 'borrowbook.html', data)
			if book_borrow.student == student:
				data['error_message'] = 'You\'re already borrow this book'
				return render(request, 'borrowbook.html', data)
			elif book_borrow.status == 'BW':
				data['error_message'] = 'Book is not available'
				return render(request, 'borrowbook.html', data)
			elif book_amount >= BOOK_LIMIT:
				data['error_message'] = 'You borrowed book limit is full!'
				return render(request, 'borrowbook.html', data)
			else:
				book_borrow.student = student
				book_borrow.status = 'BW'
				book_borrow.borrow_date = datetime.now()
				book_borrow.save()
				new_transaction = Transaction(date = datetime.now(), status='BR',
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
	start_date = datetime.now()
	stop_date = datetime.now()-timedelta(days=30)
	range_transactions = Transaction.objects.all().filter(date__range=(stop_date, start_date))
	cates = BookCategories.objects.all().filter(~Q(name = 'DeleteCat'))
	graph = {'name':[], 'amount':[]} #Total Book <Catagories>
	graph2 = {'name':['At Library', 'Borrowed'], 'amount':[]} #Total Book <Status>
	graph3 = {'name':[], 'amount':[]} #Total Borrowed Book last 30 days
	graph4 = {'name':['Borrow', 'Return'], 'amount':[]}
	graph2['amount'] = [len(Book.objects.all().filter(status='AL')),len(Book.objects.all().filter(status='BW'))]
	graph4['amount'] = [len(range_transactions.filter(status='BR')),len(range_transactions.filter(status='RT'))]
	for cate in cates:
		graph['name'].append(cate.name)
		graph3['name'].append(cate.name)
		graph['amount'].append(len(Book.objects.all().filter(category=cate)))
		count = 0
		for transactions in range_transactions.filter(status = 'BR'):
			if(transactions.book.category == cate):
				count += 1
		graph3['amount'].append(count)
	color_list = ['#607D8B','#FFEB3B','#FFC107','#FF5722','#795548','#CDDC39','#8BC34A','#4CAF50','#009688','#00BCD4','#03A9F4','#2196F3','#3F51B5','#673AB7','#9C27B0','#E91E63','#F44336']
	random.shuffle(color_list)
	data['graph'] = graph
	data['graph2'] = graph2
	data['graph3'] = graph3
	data['graph4'] = graph4
	data['shuffle_color_list'] = color_list
	try:
		data['transactions'] = Transaction.objects.order_by('-date')[:30]
	except:
		data['transactions'] = []
	return render(request, 'backend_home.html', data)

@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def backend_addbook(request):
	data = {'page': 'BookManager'}
	data['user'] = request.user
	if request.method == 'POST':
		if 'book_search' in request.POST:
			s_status = request.POST.get('status', False)
			s_category = request.POST.get('category_name', False)
			del_cata = BookCategories.objects.get(name = 'DeleteCat')
			book_list = Book.objects.all().filter(~Q(category = del_cata))
			if s_status != 'all':
				book_list = book_list.filter(status = s_status)
			if s_category != 'all':
				cata = BookCategories.objects.get(name = s_category)
				book_list = book_list.filter(category = cata)
			if s_category == 'DeleteCat' or s_status == 'DL':
				book_list = Book.objects.all().filter	(category = del_cata)
			data['book_list'] = book_list
			data['Categories_list'] = BookCategories.objects.all()
			return render(request, 'backend_addbook.html', data)
		elif 'add_category' in request.POST:
			cata_name = request.POST.get('category_name')
			try:
				BookCategories.objects.get(name = cata_name)
			except:
				cata = BookCategories(name = cata_name)
				cata.save()
		elif 'delete_category' in request.POST:
			cata_name = request.POST.get('category_name')
			cata = BookCategories.objects.get(name = cata_name)
			books = Book.objects.all().filter(category = cata)
			for book in books:
				book.deleteBook()
			cata.delete()
		elif 'add_book' in request.POST:
			ab_name = request.POST.get('add_name', False)
			ab_author = request.POST.get('add_author', False)
			ab_code = request.POST.get('add_code', False)
			ab_date = request.POST.get('add_date', False)
			ab_isbn = request.POST.get('add_isbn', False)
			ab_address = request.POST.get('add_address', False)
			post_category = request.POST.get('ab_category', False)
			ab_category = BookCategories.objects.get(name = post_category)
			ab_student = Student.objects.get(student_ID = 'libraryStore')
			try:
				upload_file = request.FILES['book_image']
			except:
				upload_file = False
			new_book = Book(name = ab_name, author = ab_author, address = ab_address,
							code = ab_code, date = ab_date, student = ab_student,
							isbn = ab_isbn, category = ab_category, picture=upload_file)
			new_book.save()
		elif 'delete_book' in request.POST:
			for book_selected in request.POST.getlist('bookTable'):
				try:
					b = Book.objects.get(pk = book_selected[9:])
					b.deleteBook()
				except:
					print("Can't Delete Book")
		return HttpResponseRedirect("/lib/librarian/backend_addbook/")
	try:
		del_cata = BookCategories.objects.get(name = 'DeleteCat')
	except:
		del_cata = BookCategories(name = 'DeleteCat')
		del_cata.save()
	data['book_list'] = Book.objects.all().filter(~Q(category = del_cata))
	data['Categories_list'] = BookCategories.objects.all().filter(~Q(name = 'DeleteCat'))
	data['form'] = bookImgFileForm()
	return render(request, 'backend_addbook.html', data)

@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def backend_editBook(request, book_id):
	data = {'page': 'BookManager'}
	data['book'] = Book.objects.get(pk = book_id)
	data['form'] = bookImgFileForm()
	data['Categories_list'] = BookCategories.objects.all().filter(~Q(name = 'DeleteCat'))
	if request.method == 'POST':
		if 'edit_book' in request.POST:
			book_edit = Book.objects.get(pk = book_id)
			book_edit.name = request.POST.get('add_name', False)
			book_edit.author = request.POST.get('add_author', False)
			book_edit.code = request.POST.get('add_code', False)
			book_edit.date = request.POST.get('add_date', False)
			book_edit.isbn = request.POST.get('add_isbn', False)
			book_edit.address = request.POST.get('add_address', False)
			post_category = request.POST.get('ab_category', False)
			book_edit.category = BookCategories.objects.get(name = post_category)
			book_edit.student = Student.objects.get(student_ID = 'libraryStore')
			try:
				upload_file = request.FILES['book_image']
			except:
				upload_file = False
			book_edit.picture = upload_file
			book_edit.save()
		return HttpResponseRedirect("/lib/librarian/backend_addbook/")
	return render(request, 'backend_editbook.html', data)	


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
					b = Book.objects.all().filter(student = s)
					for book in b:
						book.deleteBook()
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
			try:
				student = Student.objects.get(student_ID = search_student)
			except:
				data['error_message'] = "Student ID Not Found"
				return render(request, 'backend_returnBook.html', data)
			book_list = Book.objects.all().filter(student = student)
			books = []
			price = []
			data['student'] = student
			for book in book_list:
				book.borrow_date += timedelta(days=BOOK_DUE_DATE)
				books.append(book)
				over = datetime.now().date()-book.borrow_date.date()
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
				new_transaction = Transaction(date = datetime.now(), status='RT',
											  student = student, book=b)
				new_transaction.save()
		return HttpResponseRedirect("/lib/librarian/backend_returnbook/")
	return render(request, 'backend_returnBook.html', data)