from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('scripts/', views.script_list, name='script_list'),
    path('generate-script/', views.generate_script, name='generate_script'),
]