# Create your views here.
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template import loader
from social_django.utils import load_strategy
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import biblio.models as biblio


@login_required
def index(request):
    template = loader.get_template('biblio.html')

    if 'refresh' in request.POST:
        tracks = biblio.get_tracks_from_api(request)
    else:
        tracks = biblio.get_liked_tracks_from_bd(request)
        print(len(tracks))
        # paginator = Paginator(tracks, 20)

    artists = biblio.get_liked_artist_from_bd(request)

    context = {
        'tracks': tracks,
        'artists': artists,
    }

    '''
    return render(request, 'biblio.html', {'tracks': tracks,
                                               'artists': artists})
                                               '''
    return HttpResponse(template.render(context, request))


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
