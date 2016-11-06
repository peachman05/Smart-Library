from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("<h2>this is catalog view homepage</h2>")

def detail(request,book_id):
    return HttpResponse("<h3>Detail for book id : "+book_id +"</h3>")
