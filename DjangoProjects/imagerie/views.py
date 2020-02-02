from django.shortcuts import render
from django.contrib import messages
from .forms import ImportImageForm
from PIL import Image
from django.http import HttpResponse



# Create your views here.
def home(request):
    messages.debug(request, "debug")
    messages.success(request, "You successfully came here")
    messages.warning(request, "WARNING")
    return render(request, "imagerie/home.html", locals())


def import_image(request):
    form = ImportImageForm(request.POST or None, request.FILES)
    if form.is_valid():
        img = form.cleaned_data['image']
        im = Image.open(img)
        im.show()
        form.save()

        envoi = True

    return render(request, "imagerie/import_image.html", locals())


def success(request):
    return HttpResponse('successfully uploaded')
