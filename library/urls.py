"""smart_library URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from library import views
from library import catalog_views

urlpatterns = [
    # url(r'^$', views.home, name="home"),
    url(r'^$', views.home), 

    url(r'^librarian/$', views.backend_home),
    url(r'^librarian/backend_addbook/edit/(?P<book_code>([a-zA-Z0-9])+)/$', views.backend_editBook),
    url(r'^librarian/backend_addbook', views.backend_addbook),
    url(r'^librarian/backend_user', views.backend_user),
    url(r'^librarian/backend_setting', views.backend_setting),
    url(r'^librarian/backend_returnbook', views.backend_returnbook),
    url(r'^borrow/(?P<book_code>([a-zA-Z0-9])+)/$', views.borrowBookByCode),
    url(r'^borrow', views.borrowBook),
    url(r'^setting', views.setting),
    url(r'^catalog/$', catalog_views.index, name='catalog_home'),
    url(r'^catalog/(?P<book_id>[0-9]+)/$', catalog_views.detail, name='detail')
]
