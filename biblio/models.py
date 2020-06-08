import itertools
import logging
import time
import json

from gevent import monkey
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, IntegrityError
from biblio.views import get_access_token, refresh_access_token


def stub(*args, **kwargs):  # pylint: disable=unused-argument
    pass


monkey.patch_all = stub
import grequests
import requests


class Track(models.Model):
    id_track = models.CharField(max_length=24, null=False, unique=True)
    title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    album = models.CharField(max_length=100)
    url_cover_small = models.SlugField(max_length=100)
    url_cover_medium = models.SlugField(max_length=100)
    url_cover_large = models.SlugField(max_length=100)
    url_track = models.SlugField(max_length=100)
    url_player = models.SlugField(max_length=100, null=True)
    # artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    # album = models.ForeignKey(Album, on_delete=models.CASCADE)


class LikedTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_song = models.ForeignKey(Track, on_delete=models.CASCADE, null=False)
    date_added = models.DateTimeField()


class Artist(models.Model):
    id_artist = models.CharField(max_length=25, null=False, unique=True)
    name = models.CharField(max_length=100, null=False)


class LikedArtist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=False)
    related_track = models.ForeignKey(Track, on_delete=models.CASCADE, null=False)


class Album(models.Model):
    id_album = models.CharField(max_length=25, default='')
    name = models.CharField(max_length=100, default='')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)


def delete_all_tracks():
    Track.objects.all().delete()
    LikedTrack.objects.all().delete()


# Récupérer les chansons d'un utilisateur via l'API
@login_required
def get_tracks_from_api(request):
    liked_tracks = LikedTrack.objects.filter(user=request.user)
    try:
        response = requests.get('https://api.spotify.com/v1/me/tracks',
                                params={'access_token': get_access_token(request),
                                        'limit': 50})
        data = response.json()
        total = data['total']
    except KeyError:
        response = requests.get('https://api.spotify.com/v1/me/tracks',
                                params={'access_token': refresh_access_token(request),
                                        'limit': 50})
        data = response.json()
        total = data['total']
    except ConnectionError:
        return 'Problème de connexion'
    except ObjectDoesNotExist:
        return 'Introuvable'
    if total != liked_tracks.count():
        liked_tracks.delete()
        offset = 0
        urls = []
        while offset < total:
            urls.append('https://api.spotify.com/v1/me/tracks?offset=' + str(offset) + '&limit=50')
            offset += 50
        params = {'access_token': get_access_token(request)}
        start_time = time.time()
        rs = (grequests.get(u, params=params) for u in urls)
        results = grequests.map(rs)
        print("mapping-- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()
        item_object_list = [item for result in results for item in result.json()['items']]
        '''
        for result in results:
            result = result.json()
            for item in result['items']:
                item_object_list.append(item)
        '''
        print("traitement-- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()
        track_object_list = [Track(
            id_track=item['track']['id'],
            title=item['track']['name'],
            artist=item['track']['artists'][0]['name'],
            album=item['track']['album']['name'],
            url_cover_small=get_album_covers(item['track']['album']['images'])[0],
            url_cover_medium=get_album_covers(item['track']['album']['images'])[1],
            url_cover_large=get_album_covers(item['track']['album']['images'])[2],
            url_track=item['track']['external_urls']['spotify'],
            url_player=item['track']['preview_url'],
        ) for item in item_object_list]
        Track.objects.bulk_create(track_object_list, ignore_conflicts=True)

        liked_artist_object_list = []
        liked_track_object_list = []
        for item in item_object_list:
            liked_track = LikedTrack(
                user=request.user,
                user_song=Track.objects.get(id_track=item['track']['id']),
                date_added=item['added_at'],
            )
            liked_track_object_list.append(liked_track)
            for artist in item['track']['artists']:
                if artist['type'] == "artist":
                    try:
                        artist_object, artist_created = Artist.objects.get_or_create(id_artist=artist['id'], name=artist['name'])
                        if artist_created:
                            liked_artist_object = LikedArtist(
                                user=request.user,
                                liked_artist=artist_object,
                                related_track=Track.objects.get(id_track=item['track']['id']),
                            )
                            liked_artist_object_list.append(liked_artist_object)
                    except IntegrityError:
                        print('Artiste '+artist['name']+' déjà existant')
                        continue

        print("creer objets-- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()
        LikedTrack.objects.bulk_create(liked_track_object_list)
        LikedArtist.objects.bulk_create(liked_artist_object_list)
        print("bulk objets-- %s seconds ---" % (time.time() - start_time))
    track_list = get_liked_tracks_from_bd(request)
    return track_list


def get_album_covers(images):
    try:
        cover_small = images[2]['url']
        cover_medium = images[1]['url']
        cover_large = images[0]['url']
    except IndexError:
        cover_small = cover_medium = cover_large = 'https://upload.wikimedia.org/wikipedia/commons/thumb' \
                                                   '/8/80/Circle-icons-music.svg/512px-Circle-icons-music' \
                                                   '.svg.png '
    return [cover_small, cover_medium, cover_large]


# Obtenir l'inventaire des chansons pour un certain utilisateur
@login_required
def get_liked_tracks_from_bd(request):
    tracks = Track.objects.filter(
        id__in=LikedTrack.objects.filter(user=request.user).values_list('user_song', flat=True)
        # .order_by('date_added')
    )
    return tracks


# Obtenir l'inventaire des chansons pour un certain utilisateur
@login_required
def get_liked_artist_from_bd(request):
    list_liked_artists = LikedArtist.objects.filter(user=request.user).values_list('liked_artist', flat=True)
    artists = Artist.objects.filter(id__in=list_liked_artists)
    return artists
