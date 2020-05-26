from django.urls import path

from . import views

urlpatterns = [
    path('inscription/', views.SignUp.as_view(), name='signup'),
    path('profile/', views.index, name='profile'),
]
