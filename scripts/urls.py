from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate-script/', views.generate_script, name='generate_script'),
    path('scripts/', views.script_list, name='script_list'),
]
