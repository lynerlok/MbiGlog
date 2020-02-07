from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import ImportImageForm
from .models import Request, AlexNet


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
                alex = AlexNet.objects.filter(specialized_organ=plant_organ,
                                              specialized_background=background_type).order_by('-date').first()
                alex.classify(cnns[plant_organ, background_type])
            envoi = True
            return redirect('img_view_predictions', r.pk)
    else:
        formset = ImageFormSet()
    return render(request, "imagerie/import_image.html", locals())


def success(request):
    return HttpResponse('successfully uploaded')


def view_predictions(request, id_request):
    r = Request.objects.get(pk=id_request)
    return render(request, "imagerie/view_predictions.html", locals())
