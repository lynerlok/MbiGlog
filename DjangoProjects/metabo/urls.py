from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                path('ngs_input/', views.upload_ngs_file, name='mtb_ngs'),
                path('', views.home, name="mtb_home"),
                path('cytoscape/', views.graph, name="mtb_graph"),
                path('visualize/', views.visualize, name="mtb_visu")
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
