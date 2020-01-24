from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="ngs_home"),
    # path('fastqc/', views.fastqc, name="ngs_fastqc_button"),
]
