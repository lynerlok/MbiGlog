from django.forms import formset_factory
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ImportImageForm
from .models import Request, AlexNet, Specie


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


def view_predictions(request, id_request):
    r = Request.objects.get(pk=id_request)
    return render(request, "imagerie/view_predictions.html", locals())


def specie_detail(request, specie_slug):
    specie = get_object_or_404(Specie, slug=specie_slug)
    taxons = [specie]
    taxon = specie
    while taxon.sup_taxon:
        taxons.append(taxon.sup_taxon)
        taxon = taxon.sup_taxon
    taxons.reverse()
    return render(request, "imagerie/specie_info.html", locals())
