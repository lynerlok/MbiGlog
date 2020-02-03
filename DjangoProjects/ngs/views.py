from django.shortcuts import render
from django.contrib import messages


# Create your views here.
def home(request):
    messages.success(request, "You successfully came here !")
    return render(request, "ngs/home.html", locals())
