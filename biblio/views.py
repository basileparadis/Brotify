# Create your views here.
import requests
import time
from django.core.exceptions import ObjectDoesNotExist
from social_django.utils import load_strategy
from biblio.models import Biblio, Track, Album, Artist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect


@login_required
def index(request):
    tracks = get_tracks(request)
    return render(request, 'biblio.html', {'tracks': tracks})


@login_required
def get_access_token(request):
    user = request.user
    social = user.social_auth.get(provider='spotify')
    access_token = social.get_access_token(load_strategy())
    return access_token


@login_required
def refresh_access_token(request):
    user = request.user
    social = user.social_auth.get(provider='spotify')
    strategy = load_strategy()
    social.refresh_token(strategy)
    access_token = social.extra_data['access_token']
    return access_token


@login_required
def get_tracks(request):
    try:
        response = requests.get('https://api.spotify.com/v1/me/tracks',
                                params={'access_token': get_access_token(request),
                                        'limit': 50})
        data = response.json()
        if data['total'] == len(Biblio.__call__().get_chansons()):
            pass
        else:
            Biblio.__call__().vider_biblio()
            Biblio.__call__().ajouter_chansons(data)
    except KeyError:
        response = requests.get('https://api.spotify.com/v1/me/tracks',
                                params={'access_token': refresh_access_token(request),
                                        'limit': 50})
        data = response.json()
        if data['total'] == len(Biblio.__call__().get_chansons()):
            pass
        else:
            Biblio.__call__().vider_biblio()
            Biblio.__call__().ajouter_chansons(data)
    except ObjectDoesNotExist:
        return 'Introuvable'

    if data['total'] != len(Biblio.__call__().get_chansons()):
        total = data['total']
        while data['next'] and data['offset'] < total:
            # On met un délai pour éviter ConnectionResetError
            time.sleep(1)
            response = requests.get(data['next'], params={'access_token': get_access_token(request)})
            data = response.json()
            Biblio.__call__().ajouter_chansons(data)
            print(data['offset'])
            print(str(round((int(data['offset']) / int(total) * 100), 2)) + '%')
    return Biblio.__call__().get_chansons()


'''
for artiste in les_artistes:
    id_artist = artiste['id']
    # L'artiste de la chanson
    musician = Artist.objects.create(
        id_artist=id_artist,
        name=artiste['name'])
for album in les_albums:
    id_artist = album['id']
    # L'artiste de la chanson
    musician = Artist.objects.create(
        id_album=id_artist,
        name=album['name'])
    # L'album de la chanson
    album = Album.objects.create(
        id_album=tracks_data['items'][i]['track']['album']['id'],
        name=tracks_data['items'][i]['track']['album']['name'],
        artist=musician)
'''
