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
    # user_songs = models.ForeignKey('app_label.Track', on_delete=models.CASCADE)
    liste_chansons = []
    # savedAlbums = {}
    # followedArtists = {}

    def vider_biblio(self):
        try:
            # Biblio.__call__().objects.all().delete()
            del self.liste_chansons[:]
        except Exception as exception:
            print(exception)

    def get_chansons(self):
        return self.liste_chansons

    def ajouter_chansons(self, data):
        for i in range(0, len(data['items'])):
            les_chansons = data['items'][i]['track']
            # Si la chanson n'a pas de pochette, on en attribue une générique
            try:
                cover = les_chansons['album']['images'][1]['url']
            except IndexError:
                cover = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Circle-icons-music.svg/' \
                        '512px-Circle-icons-music.svg.png'
            # La chanson
            track = Track.objects.create(
                id_track=les_chansons['id'],
                title=les_chansons['name'],
                artist=les_chansons['artists'][0]['name'],
                album=les_chansons['album']['name'],
                url_cover=cover,
                url_track=les_chansons['external_urls']['spotify'],
            )

            Biblio.__call__().get_chansons().append(track)


class Artist(models.Model):
    id_artist = models.CharField(max_length=25, default='')
    name = models.CharField(max_length=100, default='')
    # image = models.ImageField(upload_to='profile_image', blank=True)


class Album(models.Model):
    id_album = models.CharField(max_length=25, default='')
    name = models.CharField(max_length=100, default='')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    # image = models.ImageField(upload_to='profile_image', blank=True)
