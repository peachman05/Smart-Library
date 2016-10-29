from django.db import models
from django.conf import settings

# Create your models here.

class Student(models.Model):
	student_ID = models.CharField(max_length=20)
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	is_librarian = models.BooleanField(default=False)



############ Book ######################
class BookCatagories(models.Model):
	name = models.CharField(max_length=20)

class Book(models.Model):
	BOOK_STATUS = (
		('AL', 'At Library'),
		('BW', 'Borrowed'),
	)	
	name = models.CharField(max_length=70)
	author = models.CharField(max_length=50)
	code = models.CharField(max_length=20)
	date = models.DateTimeField('date published')
	isbn = models.CharField(max_length=20)
	catagory = models.ForeignKey(BookCatagories)
	status = models.CharField(max_length=2, choices=BOOK_STATUS, default='AL')


######### Transaction ##############

class Transaction(models.Model):
	date = models.DateTimeField('date published')
	TRANSACTION_STATUS = (
		('BR', 'Borrow'),
		('RT', 'Return'),
	)
	status = models.CharField(max_length=2, choices=TRANSACTION_STATUS, default='RT')
	student = models.ForeignKey(Student)
	book = models.ForeignKey(Book)
# Create your models here.
