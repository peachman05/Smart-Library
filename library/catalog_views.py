from django.shortcuts import render
from django.http import HttpResponse
from .models import Book


def index(request):
    if request.method == 'POST':
        search = request.POST['search']
        # all_books = Book.objects.get(Book.name=search)
        all_books = Book.objects.filter(name__icontains=search)
        return render(request, 'catalog.html', {'all_books': all_books})
    else:
        all_books = Book.objects.all()
        return render(request, 'catalog.html', {'all_books': all_books})


def detail(request, book_id):
    return HttpResponse("<h3>Detail for book id : " + book_id + "</h3>")
