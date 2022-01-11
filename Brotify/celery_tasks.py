from __future__ import absolute_import, unicode_literals

import os
import time

import grequests
import requests
from celery import Celery, shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from social_django.utils import load_strategy
from celery_progress.backend import ProgressRecorder

from biblio.models import LikedTrack, Track, get_album_covers, Artist, LikedArtist

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Brotify.settings')

app = Celery('Brotify')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@shared_task(bind=True)
def get_tracks_from_api(self, user):

    progress_recorder = ProgressRecorder(self)
    liked_tracks = LikedTrack.objects.filter(user=user)
    try:
        response = requests.get('https://api.spotify.com/v1/me/tracks',
                                params={'access_token': get_access_token(user),
                                        'limit': 50})
        data = response.json()
        total = data['total']
    except KeyError:
        response = requests.get('https://api.spotify.com/v1/me/tracks',
                                params={'access_token': refresh_access_token(user),
                                        'limit': 50})
        data = response.json()
        total = data['total']
    except ConnectionError:
        return 'Problème de connexion'
    except ObjectDoesNotExist:
        return 'Introuvable'
    if total == liked_tracks.count():
        progress_recorder.set_progress(liked_tracks.count(), total)
    else:
        liked_tracks.delete()
        current = 0
        offset = 0
        urls = []
        while offset < total:
            urls.append('https://api.spotify.com/v1/me/tracks?offset=' + str(offset) + '&limit=50')
            offset += 50
        params = {'access_token': get_access_token(user)}
        start_time = time.time()
        rs = (grequests.get(u, params=params) for u in urls)
        results = grequests.map(rs)
        print("mapping-- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()
        item_object_list = [item for result in results for item in result.json()['items']]
        progress_recorder.set_progress(current, len(item_object_list))

        print("traitement-- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()

        track_object_list = []
        for item in item_object_list:
            track_object_list.append(Track(
                spotify_id=item['track']['id'],
                title=item['track']['name'],
                artist=item['track']['artists'][0]['name'],
                album=item['track']['album']['name'],
                url_cover_small=get_album_covers(item['track']['album']['images'])[0],
                url_cover_medium=get_album_covers(item['track']['album']['images'])[1],
                url_cover_large=get_album_covers(item['track']['album']['images'])[2],
                url_track=item['track']['external_urls']['spotify'],
                url_player=item['track']['preview_url'],
            ))
            current += 1
            progress_recorder.set_progress(current, len(item_object_list))
        Track.objects.bulk_create(track_object_list, ignore_conflicts=True)

        liked_artist_object_list = []
        liked_track_object_list = []
        for item in item_object_list:
            liked_track = LikedTrack(
                user=user,
                user_song=Track.objects.get(spotify_id=item['track']['id']),
                date_added=item['added_at'],
            )
            liked_track_object_list.append(liked_track)
            for artist in item['track']['artists']:
                if artist['type'] == "artist":
                    try:
                        artist_object, artist_created = Artist.objects.get_or_create(spotify_id=artist['id'],
                                                                                     name=artist['name'])
                        liked_artist_object = LikedArtist(
                            user=user,
                            liked_artist=artist_object,
                            related_track=Track.objects.get(spotify_id=item['track']['id']),
                        )
                        liked_artist_object_list.append(liked_artist_object)
                    except IntegrityError:
                        print('Artiste ' + artist['name'] + ' déjà existant')
                        continue

        print("creer objets-- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()
        LikedTrack.objects.bulk_create(liked_track_object_list)
        LikedArtist.objects.bulk_create(liked_artist_object_list)
        print("bulk objets-- %s seconds ---" % (time.time() - start_time))

    return 0


def get_access_token(user):
    social = user.social_auth.get(provider='spotify')
    access_token = social.get_access_token(load_strategy())
    return access_token


def refresh_access_token(user):
    social = user.social_auth.get(provider='spotify')
    strategy = load_strategy()
    social.refresh_token(strategy)
    access_token = social.extra_data['access_token']
    return access_token
