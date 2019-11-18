from django.shortcuts import render


# Create your views here.
def home(request):
    a = 5
    return render(request, "imagerie/home.html", locals())
