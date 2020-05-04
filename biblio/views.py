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


def api_request_to_json(url, access_token):
    response = requests.get(url, params={'access_token': access_token})
    data = response.json()
    return data


@login_required
def get_tracks(request):
    global list_tracks
    try:
        list_tracks = []
        data = api_request_to_json('https://api.spotify.com/v1/me/tracks', get_access_token(request))
        for i in range(0, len(data['items'])):
            # les_artistes = tracks_data['items'][i]['track']['artists']
            # les_albums = tracks_data['items'][i]['track']['album']
            les_chansons = data['items'][i]['track']
            # La chanson
            track = Track.objects.create(
                # id_track=chanson['id'],
                id_track=les_chansons['id'],
                title=les_chansons['name'],
                artist=les_chansons['artists'][0]['name'],
                album=les_chansons['album']['name'],
                url_cover=les_chansons['album']['images'][1]['url'],
                url_track=les_chansons['external_urls']['spotify'],
            )
            list_tracks.append(track)
    except KeyError:
        data = api_request_to_json('https://api.spotify.com/v1/me/tracks', refresh_access_token(request))
        for i in range(0, len(data['items'])):
            # les_artistes = tracks_data['items'][i]['track']['artists']
            # les_albums = tracks_data['items'][i]['track']['album']
            les_chansons = data['items'][i]['track']
            # La chanson
            track = Track.objects.create(
                # id_track=chanson['id'],
                id_track=les_chansons['id'],
                title=les_chansons['name'],
                artist=les_chansons['artists'][0]['name'],
                album=les_chansons['album']['name'],
                url_cover=les_chansons['album']['images'][1]['url'],
                url_track=les_chansons['external_urls']['spotify'],
            )
            list_tracks.append(track)
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
    except ObjectDoesNotExist:
        return 'Introuvable'
    return list_tracks


@login_required
def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'spotify':
        profile = user.get_profile()
        if profile is None:
            profile = Biblio(user_id=user.id)
        profile.gender = response.get('gender')
        profile.link = response.get('link')
        profile.timezone = response.get('timezone')
        profile.save()


@login_required
def settings(request):
    user = request.user
    try:
        spotify_login = user.social_auth.get(provider='spotify')
    except:
        spotify_login = None

    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

    return render(request, 'core/settings.html', {
        'spotify_login': spotify_login,
        'can_disconnect': can_disconnect
    })


@login_required
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    return render(request, 'core/password.html', {'form': form})
