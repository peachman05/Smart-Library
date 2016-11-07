from django.shortcuts import render
from django.http import HttpResponse
from .models import Book, BookCatagories
from django.db.models import Q


def index(request):

    if request.method == 'POST':
        search = request.POST['search']
        del_cata = BookCatagories.objects.get(name='DeleteCat')
        book_list = Book.objects.all().filter(~Q(catagory=del_cata))
        book_list = book_list.filter(name__icontains=search)
        all_catagory = BookCatagories.objects.all().filter(~Q(name=del_cata.name))
        return render(request, 'catalog.html', {'all_books': book_list , 'all_catagory': all_catagory})
    else:
        del_cata = BookCatagories.objects.get(name='DeleteCat')
        book_list = Book.objects.all().filter(~Q(catagory=del_cata))
        all_catagory = BookCatagories.objects.all().filter(~Q(name=del_cata.name))
        return render(request, 'catalog.html', {'all_books': book_list , 'all_catagory': all_catagory})


def detail(request, book_id):
    # return HttpResponse("<h3>Detail for book id : " + book_id + "</h3>")
    return render(request, 'catalog_detail.html', {})
