from django.shortcuts import render
from django.http import HttpResponse, Http404
from .models import Book, BookCategories
from django.db.models import Q


def index(request):

    if request.method == 'POST':
        search = request.POST['search']
        del_cata = BookCategories.objects.get(name='DeleteCat')
        book_list = Book.objects.all().filter(~Q(category=del_cata))
        book_list = book_list.filter(name__icontains=search)
        all_category = BookCategories.objects.all().filter(~Q(name=del_cata.name))
        return render(request, 'catalog.html', {'all_books': book_list, 'all_category': all_category, 'search': search})
    else:
        del_cata = BookCategories.objects.get(name='DeleteCat')
        book_list = Book.objects.all().filter(~Q(category=del_cata))
        all_category = BookCategories.objects.all().filter(~Q(name=del_cata.name))
        return render(request, 'catalog.html', {'all_books': book_list, 'all_category': all_category})


def detail(request, book_id):
    try:
        book = Book.objects.get(pk=book_id)
        book_address = book.address[:3]
    except Book.DoesNotExist:
        raise Http404("Book does not exist")
    # return HttpResponse("<h3>Detail for book id : " + book_id + "</h3>")
    return render(request, 'catalog_detail.html', {'book': book, 'book_address': book_address})
