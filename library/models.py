from django.db import models
from django.conf import settings

# Create your models here.

class Student(models.Model):
	student_ID = models.CharField(max_length=20)
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	is_librarian = models.BooleanField(default=False)
	def __str__(self):
		return self.student_ID + ':  ' + self.user.first_name + " " + self.user.last_name



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
            return len(Transaction.objects.filter(book__category__name = category_name))

	def booknameCount(book_name):
            return len(Transaction.objects.filter(book__name = book_name))

	def __str__(self):
		return self.book.name

	class Meta:
		ordering = ['date']

