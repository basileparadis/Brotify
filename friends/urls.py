from django.urls import path
from . import views

urlpatterns = [
    path('amis/', views.index, name='amis'),
    path('amis/<friend_username>/', views.compare, name='compare-friend'),
    path('amis/<friend_username>/compare_tracks', views.compare_tracks, name='compare-tracks'),
    path('amis/<friend_username>/compare_artists', views.compare_artists, name='compare_artists'),
]
