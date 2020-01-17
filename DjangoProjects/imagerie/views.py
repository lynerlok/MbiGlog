from django.shortcuts import render
from django.contrib import messages


# Create your views here.
def home(request):
    messages.debug(request, "debug")
    messages.success(request, "success")
    messages.warning(request, "WARNING")
    messages.error(request, "ERROR")
    return render(request, "imagerie/home.html", locals())
