from django.shortcuts import render
import xml.etree.ElementTree as ET
import requests

# Create your views here.
def home(request):
    return render(request, "metabo/home.html", locals())
