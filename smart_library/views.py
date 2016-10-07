from django.http import HttpResponse, HttpResponseRedirect

def home(request):
  return HttpResponse("<h1>This is Smart Library</h1>")