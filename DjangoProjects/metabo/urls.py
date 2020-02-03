from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="mtb_home"),
    path('cytoscape/', views.graph, name="mtb_graph"),
]