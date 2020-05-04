from django.db import models
# Create your models here.
from django.contrib.auth.models import User
import requests
import time


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Track(models.Model):
    id_track = models.CharField(max_length=24, default='')
    title = models.CharField(max_length=100, default='')
    artist = models.CharField(max_length=100, default='')
    album = models.CharField(max_length=100, default='')
    url_cover = models.CharField(max_length=100, default='')
    url_track = models.CharField(max_length=100, default='')
    # artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    # album = models.ForeignKey(Album, on_delete=models.CASCADE)


class Biblio(metaclass=Singleton):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_songs = models.ForeignKey(Track, related_name='user_songs', on_delete=models.CASCADE)
    savedTracks = {}
    savedAlbums = {}
    followedArtists = {}

    def receive_info(self, sender, instance, created, **kwargs):
        user = User.objects.get(username=self.request.user.get_username())
        # social = user.social_auth.get(provider='spotify-oauth2')
        response = requests.get(
            'https://api.spotify.com/v1/me/tracks',
            data={'access_token': self.get_token(user)}
        )
        friends = response.json()['items']
        print("amis" + user)


class Artist(models.Model):
    id_artist = models.CharField(max_length=25, default='')
    name = models.CharField(max_length=100, default='')
    # image = models.ImageField(upload_to='profile_image', blank=True)


class Album(models.Model):
    id_album = models.CharField(max_length=25, default='')
    name = models.CharField(max_length=100, default='')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    # image = models.ImageField(upload_to='profile_image', blank=True)
