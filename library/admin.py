from django.contrib import admin
from .models import Student, BookCategories, Book, Transaction
# Register your models here.


class StudentAdmin(admin.ModelAdmin):
	fields = ['student_ID', 'user', 'is_librarian']

admin.site.register(Student, StudentAdmin),
admin.site.register(BookCategories),
admin.site.register(Book),
admin.site.register(Transaction),
