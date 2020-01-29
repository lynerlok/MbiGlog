from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.import_image, name="img_home"),
    path('import_image/', views.import_image, name="img_import"),


]