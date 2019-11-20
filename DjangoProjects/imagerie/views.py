from django.shortcuts import render
from django.contrib import messages


# Create your views here.
def home(request):
    a = 5
    messages.debug(request, "debug")
    messages.info(request, f'a value is {a}')
    messages.success(request, "success")
    messages.warning(request, "WARNING")
    messages.error(request, "ERROR")
    return render(request, "imagerie/home.html", locals())
