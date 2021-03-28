# Create your views here.
from celery.bin import celery
from django.core.paginator import Paginator
import biblio.models as biblio
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from Brotify.celery_tasks import get_tracks_from_api


@login_required
def index(request):
    template = loader.get_template('biblio.html')

    id_task = None
    if 'refresh' in request.POST:
        id_task = get_tracks_from_api.delay(request.user)

    context = {
        'tracks': biblio.get_liked_tracks_from_bd(request),
        'artists': biblio.get_liked_artist_from_bd(request),
        'task_id': id_task,
    }

    return HttpResponse(template.render(context, request))


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
