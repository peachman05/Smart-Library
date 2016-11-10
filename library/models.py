from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
import string
import random
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta


# Create your models here.

class Student(models.Model):
	student_ID = models.CharField(max_length=20)
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	is_librarian = models.BooleanField(default=False)
	def __str__(self):
		return self.student_ID + ':  ' + self.user.first_name + " " + self.user.last_name
	def generateNewPassword(self):
		passwd = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(9))
		mail_message = 'Dear '+self.user.first_name+' '+self.user.last_name
		mail_message += '\n\n\n\t Your password is reset!!\n\t So your new password is: '+passwd
		mail_message += '\n\n\nThank, \nSmart-Library Teams.'
		email = self.user.email
		send_mail(
			'Your Account\'s password is reset!',
			mail_message,
			settings.EMAIL_HOST_USER,
			[email],
			fail_silently=True,
		)
		self.user.set_password(passwd)
		self.user.save()
	def setNewPassword(self, passwd):
		self.user.set_password(passwd)
		self.user.save()
		mail_message = 'Dear '+self.user.first_name+' '+self.user.last_name
		mail_message += '\n\n\n\t Your Account\'s Password is Changed. (Account: '+self.user.username
		mail_message += ')\n\n\nThank, \nSmart-Library Teams.'
		send_mail(
			'Your Password Is Changed!',
			mail_message,
			settings.EMAIL_HOST_USER,
			[self.user.email],
			fail_silently=True,
		)
############ Book ######################
class BookCategories(models.Model):
	name = models.CharField(max_length=20)
	def __str__(self):
		return self.name

class Book(models.Model):
	BOOK_STATUS = (
		('AL', 'At Library'),
		('BW', 'Borrowed'),
		('DL', 'Deleted'),
	)	
	name = models.CharField(max_length=70)
	author = models.CharField(max_length=50)
	code = models.CharField(max_length=20)
	date = models.CharField(max_length=50)
	isbn = models.CharField(max_length=20)
	address = models.CharField(max_length=20)
	category = models.ForeignKey(BookCategories)
	borrow_date = models.DateTimeField('borrow', null=True, blank=True)
	picture = models.FileField(upload_to='library/bookpic/', blank=True)
	status = models.CharField(max_length=2, choices=BOOK_STATUS, default='AL')
	student = models.ForeignKey(Student)
	def __str__(self):
		return self.name + ':  ' + self.author
	def deleteBook(self):
		self.status = 'DL'
		try:
			del_cata = BookCategories.objects.get(name = 'DeleteCat')
		except:
			del_cata = BookCategories(name = 'DeleteCat')
			del_cata.save()
		libStudent = Student.objects.get(student_ID = 'libraryStore')
		new_Transaction = Transaction(date = datetime.datetime.now(), status='DL', student = libStudent, book=self)
		new_Transaction.save()
		self.category = del_cata
		self.save()

######### Transaction ##############

class Transaction(models.Model):
	date = models.DateTimeField('transaction date')
	TRANSACTION_STATUS = (
		('BR', 'Borrow'),
		('RT', 'Return'),
		('DL', 'Delete'),
	)
	status = models.CharField(max_length=2, choices=TRANSACTION_STATUS, default='RT')
	student = models.ForeignKey(Student)
	book = models.ForeignKey(Book)


	def categoryCount(category_name):
			dateThreshold = datetime.now() - timedelta(days=30) 
			return len(Transaction.objects.filter(book__category__name = category_name , date__gte = dateThreshold  , status = 'BR'  ))

	def booknameCount(book_name):
            dateThreshold = datetime.now() - timedelta(days=30) 
            return len(Transaction.objects.filter(book__name = book_name , date__gte = dateThreshold  , status = 'BR'  ))
            #return len(Transaction.objects.filter(book__name = book_name ))

	def __str__(self):
		return self.book.name

	class Meta:
		ordering = ['date']

