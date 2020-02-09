from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.import_image, name="img_home"),
    path('results-of-<int:id_request>', views.view_predictions, name="img_view_predictions"),
    path('<slug:specie_slug>-info', views.specie_detail, name='img-specie-detail')

]
