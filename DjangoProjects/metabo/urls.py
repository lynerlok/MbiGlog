from django.contrib import admin
from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [path('ngs/',views.upload_file, name='mtb_ngs'),
                  path('', views.home, name="mtb_home"),
                  path('cytoscape/', views.graph, name="mtb_graph"),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
