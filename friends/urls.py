from django.urls import path
from . import views

urlpatterns = [
    path('amis/', views.index, name='amis'),
]