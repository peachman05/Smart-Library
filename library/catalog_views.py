from django.shortcuts import render
from django.http import HttpResponse
from .models import Book

def index(request):
    all_books = Book.objects.all()
    return render(request, 'catalog.html', {'all_books': all_books})

def detail(request,book_id):
    return HttpResponse("<h3>Detail for book id : "+book_id +"</h3>")
