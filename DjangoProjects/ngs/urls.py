from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="ngs_home"),

    path('pipeline/',views.pipeline,name="ngs pipeline home"),
    path('pipeline/fastqc-<int:id_request>/', views.fastqc, name="ngs fastqc"),
    path('pipeline/hisat/',views.hisat, name="hisat2"),
    path('pipeline/R_analysis/',views.ranalysis, name='R analysis'),
    path('pipeline/results/',views.results, name="Results"),

    path('proteo/fasta',views.proteo, name='Proteo fasta'),

    path('phylo_hub/align', views.phylo_align, name="phylogenic pipeline align"),
    path('phylo_hub',views.phylo_hub, name="phylogenic hub"),
    path('phylo_hub/tree', views.phylo_tree, name="phylogenic compute tree"),
    path('phylo_hub/visu', views.phylo_visu, name="phylogenic visualization")
]
