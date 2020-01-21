from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="prt_home"),
    path('1D/', views.Onedimension, name="one_dimension"),
]
