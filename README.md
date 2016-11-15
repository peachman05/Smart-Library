# Smart Library

Smart Library is library management system
Using
- Python 3.5.2 *(Programming Language)*
- Django 1.10.2 *(Web Framework)*

This is project submitted to **Software Engineering subject, CE KMITL 2016**

**Contributors**
* Supawit Kansompoj
* Siridej Phanathanate
* Peerawat Pipattanakulchai
* Patcharapon Jantana
* Isara Naranirattisai



## to Install Smart Library
- Clone [Smart-Library Repo](https://github.com/DreamN/Smart-Library.git)

	```
		$git clone https://github.com/DreamN/Smart-Library.git
	```
- Install [PIP](https://pypi.python.org/pypi/pip)
- Install Django

	```
		$pip install Django==1.10.2
	```
- Install Requirement
	```
   		 $pip install -r requirements.txt
	```
- Create local_settings.py
	```
	Smart-Library/
		smart_library/
			__init__.py
			local_settings.py
			settings.py
			urls.py
			views.py
			wsgi.py
		library/
		templates/
		.gitignore
		manage.py
		requirements.txt
	```
	###Database
  and paste and code below on local_settings.py and edit for your Database then save!
	```python
	import os

	# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

	# Database
	# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
	        DATABASES = {
	            'default': {
	                'ENGINE': 'django.db.backends.postgresql',
	                'NAME': 'mydatabase',
	                'USER': 'mydatabaseuser',
	                'PASSWORD': 'mypassword',
	                'HOST': '127.0.0.1',
	                'PORT': '5432',
	            }
	        }
	```
  or replace with code below for sqlite3
  ```python
  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
  }
  ```
  
  ##Email setting
> **Smart Library System is required email for send generated random-password to student's email when new student account is created*
  
  code below is an example for Gmail(Also paste this setting in local_settings.py same as the same as 'database')
  ```python
    # for gmail
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'youremail@gmail.com'
    EMAIL_HOST_PASSWORD = 'yourpassword'
    EMAIL_PORT = 587
  ```
- Make Migrations

```
$ python manage.py makemigrations
```
- Migrate

```
$ python manage.py migrate
```
- Create Superuser (for access site/admin)

```
$ python manage.py createsuperuser
```
##some objects must be created before use the system
Go to [Django Admin](https://docs.djangoproject.com/en/1.10/ref/contrib/admin/) and then
* Create Student object with student id '**libraryStore**' (we use to store every 'at library' books)
* Create BookCategories with name '**DeleteCat**' (this is category which deleted book will changed catagories to)

**[Django Deployment Checklist](https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/)*

### Run Server
```
$ python manage.py runserver
```
