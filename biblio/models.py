from django.db import models

# Create your models here.
from django.contrib.auth.models import User
import requests


class Biblio(models.Model):
    # user = models.OneToOneField(User)
    description = models.CharField(max_length=100, default='')
    image = models.ImageField(upload_to='profile_image', blank=True)
    savedTracks = {}
    savedAlbums = {}
    followedArtists = {}

    def receive_info(self, sender, instance, created, **kwargs):
        user = User.objects.get(username=self.request.user.get_username())
        social = user.social_auth.get(provider='spotify-oauth2')
        response = requests.get(
            'https://api.spotify.com/v1/me/tracks',
            params={'access_token': social.extra_data['access_token']}
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


class Track(models.Model):
    id_track = models.CharField(max_length=25, default='')
    title = models.CharField(max_length=100, default='')
    artist = models.CharField(max_length=100, default='')
    album = models.CharField(max_length=100, default='')
    # artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    # album = models.ForeignKey(Album, on_delete=models.CASCADE)
