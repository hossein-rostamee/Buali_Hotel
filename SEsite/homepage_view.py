from django.shortcuts import render
from django.http.response import HttpResponse , Http404 , HttpResponseRedirect , JsonResponse

def homepage(request):
    return render(request , 'Home.html')