from django.contrib import messages
from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import render

from .forms import ImportImageForm
from .models import Request, AlexNet


# Create your views here.
def home(request):
    messages.debug(request, "debug")
    messages.success(request, "You successfully came here")
    messages.warning(request, "WARNING")
    return render(request, "imagerie/home.html", locals())


def import_image(request):
    ImageFormSet = formset_factory(ImportImageForm)
    if request.method == 'POST':
        formset = ImageFormSet(request.POST, files=request.FILES)
        if formset.is_valid():
            r = Request()
            r.save()
            cnns = {}
            for form in formset:
                submitted = form.save(commit=False)
                submitted.request = r
                submitted.save()
                if (submitted.plant_organ, submitted.background_type) not in cnns:
                    cnns[submitted.plant_organ, submitted.background_type] = [submitted]
                else:
                    cnns[submitted.plant_organ, submitted.background_type].append(submitted)
            for plant_organ, background_type in cnns:
                alex = AlexNet.objects.get(specialized_organ=plant_organ, specialized_background=background_type)
                alex.classify(cnns[plant_organ, background_type])
            envoi = True
    else:
        formset = ImageFormSet()
    row_name = "image to guess"
    return render(request, "imagerie/import_image.html", locals())


def success(request):
    return HttpResponse('successfully uploaded')
