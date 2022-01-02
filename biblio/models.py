import itertools
import logging
import time
import json

from gevent import monkey
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models


def stub(*args, **kwargs):  # pylint: disable=unused-argument
    pass


monkey.patch_all = stub
import grequests
import requests


class Track(models.Model):
    id = models.BigAutoField(primary_key=True)
    spotify_id = models.CharField(max_length=24, null=False, unique=True)
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
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_song = models.ForeignKey(Track, on_delete=models.CASCADE, null=False)
    date_added = models.DateTimeField()


class Artist(models.Model):
    id = models.BigAutoField(primary_key=True)
    spotify_id = models.CharField(max_length=25, null=False, unique=True)
    name = models.CharField(max_length=100, null=False)


class LikedArtist(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=False)
    related_track = models.ForeignKey(Track, on_delete=models.CASCADE, null=False)


class Album(models.Model):
    id = models.BigAutoField(primary_key=True)
    spotify_id = models.CharField(max_length=25, default='')
    name = models.CharField(max_length=100, default='')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)


def delete_all_tracks():
    Track.objects.all().delete()
    LikedTrack.objects.all().delete()


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
    liked_tracks = LikedTrack.objects.filter(user=request.user)\
        .values_list('user_song', flat=True)\
        .order_by('date_added')
    tracks = Track.objects.filter(
        id__in=liked_tracks
    )

    return tracks


# Obtenir l'inventaire des chansons pour un certain utilisateur
@login_required
def get_liked_artist_from_bd(request):
    list_liked_artists = LikedArtist.objects.filter(user=request.user).values_list('liked_artist', flat=True)
    artists = Artist.objects.filter(id__in=list_liked_artists)
    return artists
