from django.urls import path
from . import views

urlpatterns = [
    path('biblio', views.index, name='index'),
]