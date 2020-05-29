import logging
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
    id_artist = models.CharField(max_length=25, default='')
    name = models.CharField(max_length=100, default='')


class Album(models.Model):
    id_album = models.CharField(max_length=25, default='')
    name = models.CharField(max_length=100, default='')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)


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
        rs = (grequests.get(u, params=params) for u in urls)
        results = grequests.imap(rs)
        track_object_list = []
        liked_object_list = []
        for result in results:
            result = result.json()
            for i in range(0, len(result['items'])):
                track = Track(
                    id_track=result['items'][i]['track']['id'],
                    title=result['items'][i]['track']['name'],
                    artist=result['items'][i]['track']['artists'][0]['name'],
                    album=result['items'][i]['track']['album']['name'],
                    url_cover_small=get_album_covers(result['items'][i]['track']['album']['images'])[0],
                    url_cover_medium=get_album_covers(result['items'][i]['track']['album']['images'])[1],
                    url_cover_large=get_album_covers(result['items'][i]['track']['album']['images'])[2],
                    url_track=result['items'][i]['track']['external_urls']['spotify'],
                    url_player=result['items'][i]['track']['preview_url'],
                )
                track_object_list.append(track)
        print(len(track_object_list))
        Track.objects.bulk_create(track_object_list, ignore_conflicts=True)
        for track in track_object_list:
            liked_track = LikedTrack(
                user=request.user,
                user_song=Track.objects.get(id_track=track.id_track),
                date_added=result['items'][i]['added_at'],
            )
            liked_object_list.append(liked_track)
        LikedTrack.objects.bulk_create(liked_object_list)
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
        id__in=LikedTrack.objects.filter(user=request.user).values_list('user_song_id', flat=True)
        # .order_by('date_added')
    )
    return tracks
