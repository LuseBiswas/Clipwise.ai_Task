from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('scripts/', views.script_list, name='script_list'),
    path('export-script/<int:script_id>/txt/', views.export_script_txt, name='export_script_txt'),
    path('export-script/pdf/', views.export_script_pdf, name='export_script_pdf'),
    path('export-script/<int:script_id>/pdf/', views.export_script_pdf, name='export_script_pdf'),
]