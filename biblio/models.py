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
    id_track = models.CharField(max_length=24)
    title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    album = models.CharField(max_length=100)
    url_cover = models.CharField(max_length=100)
    url_track = models.CharField(max_length=100)
    date_added = models.DateTimeField()
    # artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    # album = models.ForeignKey(Album, on_delete=models.CASCADE)


class Biblio(models.Model):
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    user_song = models.ForeignKey(Track, related_name='user_song', on_delete=models.CASCADE, null=True)
    # user_songs = models.ForeignKey('app_label.Track', on_delete=models.CASCADE)
    # liste_chansons = []
    # savedAlbums = {}
    # followedArtists = {}

    def vider_biblio(self):
        try:
            # Biblio.__call__().objects.all().delete()
            # del self.liste_chansons[:]
            Biblio.objects.all().delete()
            Track.objects.all().delete()
        except Exception as exception:
            print(exception)


def get_chansons(user):
    # return self.liste_chansons
    # return Biblio.objects.filter(user=user).user_song_id
    # return Track.objects.filter(id__in=Biblio.objects.filter(user=user).values_list('user_song_id', flat=True))
    les_chansons = []
    tracks = Track.objects.filter(id__in=Biblio.objects.filter(user=user).values_list('user_song_id', flat=True))
    for track in tracks:
        les_chansons.append(track)
    return les_chansons


def ajouter_chansons(data, user):
    for i in range(0, len(data['items'])):
        les_chansons = data['items'][i]['track']
        # Si la chanson n'a pas de pochette, on en attribue une générique
        try:
            cover = les_chansons['album']['images'][1]['url']
        except IndexError:
            cover = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Circle-icons-music.svg/' \
                    '512px-Circle-icons-music.svg.png'
        # On ajoute la chanson si elle n'existe pas déjà dans la BD
        try:
            track = Track.objects.get(id_track=les_chansons['id'])
        except Track.DoesNotExist:
            track = Track.objects.create(
                id_track=les_chansons['id'],
                title=les_chansons['name'],
                artist=les_chansons['artists'][0]['name'],
                album=les_chansons['album']['name'],
                url_cover=cover,
                url_track=les_chansons['external_urls']['spotify'],
                date_added=data['items'][i]['added_at'],
            )
        try:
            Biblio.objects.create(user=user, user_song=track)
        except Exception as exception:
            print(exception)

            # self.get_chansons().append(track)
            # Biblio.objects.add(track)
            # Biblio.__call__().get_chansons().append(track)


class Artist(models.Model):
    id_artist = models.CharField(max_length=25, default='')
    name = models.CharField(max_length=100, default='')
    # image = models.ImageField(upload_to='profile_image', blank=True)


class Album(models.Model):
    id_album = models.CharField(max_length=25, default='')
    name = models.CharField(max_length=100, default='')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    # image = models.ImageField(upload_to='profile_image', blank=True)
