import json
import random

import numpy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from friendship.models import Friend, FriendshipRequest
from django.db import IntegrityError
from biblio.models import LikedTrack, Track, LikedArtist, Artist


@login_required
def liste_amis():
    return User.objects.all()


# On vérifie les liens d'amitié entre un utilisateur
@login_required
def get_friends(request):
    liste_amis_id = []
    friends = Friend.objects.all()
    for friend in friends:
        if request.user.id is friend.to_user_id:
            liste_amis_id.append(friend.from_user_id)
        elif request.user.id is friend.from_user_id:
            liste_amis_id.append(friend.to_user_id)
    return liste_amis_id


# On vérifie les invitations envoyées d'un utilisateur
@login_required()
def get_sent_friend_request(request):
    list_sent_invitation_id = []
    invitations = FriendshipRequest.objects.all()
    for invitation in invitations:
        if request.user.id is invitation.from_user_id:
            list_sent_invitation_id.append(invitation.to_user_id)
    return list_sent_invitation_id


# On vérifie les invitations reçus pour un certain utilisateur
@login_required()
def get_received_friend_request(request):
    list_received_invitation_id = []
    invitations = FriendshipRequest.objects.all()
    for invitation in invitations:
        if request.user.id is invitation.to_user_id:
            list_received_invitation_id.append(invitation.from_user_id)
    return list_received_invitation_id


# Accepter une demande d'amitié
@login_required
def accepter_amitie(request):
    ami_potentiel_id = int(request.POST.get('user'))
    try:
        friend_request = FriendshipRequest.objects.get(from_user=ami_potentiel_id, to_user=request.user.id)
        friend_request.accept()
    except FriendshipRequest.DoesNotExist as exception:
        print("La demande d'amitié est introuvable")
        print(exception)
    except FriendshipRequest.AlreadyFriendsError as exception:
        print("Vous êtes déjà amis")
        print(exception)


# Refuser une demande d'amitié
@login_required
def refuser_amitie(request):
    ami_potentiel_id = request.POST.get('user')
    try:
        friend_request = FriendshipRequest.objects.get(from_user=ami_potentiel_id, to_user=request.user.id)
        friend_request.reject()
    except FriendshipRequest.DoesNotExist as exception:
        print("La demande d'amitié est introuvable")
        print(exception)


# Enlever un lien d'amitié existant
@login_required
def retirer_amitie(request):
    personne_id = request.POST.get('user')
    try:
        Friend.objects.remove_friend(request.user, User.objects.get(id=personne_id))
    except User.DoesNotExist as exception:
        print("L'utilisateur est introuvable")
        print(exception)


# Envoyer une demande d'amitié
@login_required
def add_friendship(request):
    personne_id = request.POST.get('user')
    try:
        Friend.objects.add_friend(request.user, User.objects.get(id=personne_id))
    except User.DoesNotExist as exception:
        print("L'utilisateur est introuvable")
        print(exception)
    except IntegrityError as exception:
        print("La demande a déjà été créée")
        print(exception)


# Lister les morceaux communs aux deux utilisateurs
@login_required
def compare_songs(request, friend):
    # Définir les usagers
    usager = request.user
    ami = friend
    # Obtenir une liste des id des chansons d'un utilisateur (biblio)
    user_liked_tracks = LikedTrack.objects.filter(user=usager).values_list('user_song', flat=True)
    friend_liked_tracks = LikedTrack.objects.filter(user=ami).values_list('user_song', flat=True)
    # Obtenir les chansons dont le id est présent dans les deux biblios
    tracks = Track.objects.filter(Q(id__in=user_liked_tracks), Q(id__in=friend_liked_tracks))
    return tracks


# Lister les artistes communs aux deux utilisateurs
@login_required
def compare_artists(request, friend):
    print(friend)
    usager = request.user
    ami = User.objects.get(username=friend)

    user_liked_artists = LikedArtist.objects.filter(user=usager).values_list('liked_artist', flat=True)
    friend_liked_artists = LikedArtist.objects.filter(user=ami).values_list('liked_artist', flat=True)

    commonly_liked_artists = LikedArtist.objects.filter(
        Q(liked_artist__in=user_liked_artists),
        Q(liked_artist__in=friend_liked_artists)
    ).values_list('liked_artist', flat=True).distinct()

    data = []
    for artist in commonly_liked_artists:
        artist_object = Artist.objects.get(id=artist)
        liked_tracks_you = LikedArtist.objects.filter(Q(liked_artist=artist),
                                                      Q(user=usager)
                                                      ).values_list('related_track', flat=True)
        liked_tracks_friend = LikedArtist.objects.filter(Q(liked_artist=artist),
                                                         Q(user=ami)
                                                         ).values_list('related_track', flat=True)
        commonly_liked_artists_tracks = LikedTrack.objects.filter(Q(user_song__in=liked_tracks_you),
                                                                  Q(user_song__in=liked_tracks_friend)
                                                                  ).values_list('user_song',
                                                                                flat=True).distinct().count()
        if commonly_liked_artists_tracks > 0:
            data.append(
                {
                    'label': [artist_object.name],
                    'backgroundColor': "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)]),
                    'borderColor': "rgba(0,0,0,1)",
                    'data': [{'x': liked_tracks_you.count(),
                              'y': liked_tracks_friend.count(),
                              'r': numpy.log(commonly_liked_artists_tracks) * 15
                              }]
                }
            )
    data_json = {
        'type': 'bubble',
        'data': {
          'labels': 'Artistes',
          'datasets': data
        },
        'options': {
            'legend': {
                'display': False
            },
            'scales': {
                'xAxes': [{
                    'type': 'logarithmic',
                    'ticks': {
                        'display': False
                    },
                    'scaleLabel': {
                        'display': True,
                        'labelString': 'Aimés par vous',
                        'fontColor': 'black',
                        'fontStyle': 'bold',
                    }
                }],
                'yAxes': [{
                    'type': 'logarithmic',
                    'ticks': {
                        'display': False
                    },
                    'scaleLabel': {
                        'display': True,
                        'labelString': 'Aimés par '+ami.username,
                        'fontColor': 'black',
                        'fontStyle': 'bold',
                    }
                }]
            },
            'plugins': {
                'zoom': {
                    'pan': {
                        'enabled': True,
                        'mode': 'xy'
                    },
                    'zoom': {
                        'enabled': True,
                        'mode': 'xy',
                    }
                }
            }
        }
    }
    data_json = json.dumps(data_json, ensure_ascii=False)
    return data_json


def get_suggested_tracks(request, friend):
    usager = request.user
    ami = friend

    user_liked_artists = LikedArtist.objects.filter(user=usager).values_list('liked_artist', flat=True)
    friend_liked_artists = LikedArtist.objects.filter(user=ami).values_list('liked_artist', flat=True)

    commonly_liked_artists = LikedArtist.objects.filter(
        Q(liked_artist__in=user_liked_artists),
        Q(liked_artist__in=friend_liked_artists)
    ).values_list('liked_artist', flat=True).distinct()

    data = []
    for artist in commonly_liked_artists:
        liked_tracks_you = LikedArtist.objects.filter(Q(liked_artist=artist),
                                                      Q(user=usager)
                                                      ).values_list('related_track', flat=True)
        liked_tracks_friend = LikedArtist.objects.filter(Q(liked_artist=artist),
                                                         Q(user=ami)
                                                         ).values_list('related_track', flat=True)
        commonly_liked_artists_tracks = LikedTrack.objects.filter(~Q(user_song__in=liked_tracks_you),
                                                                  Q(user_song__in=liked_tracks_friend)
                                                                  ).values_list('user_song', flat=True).distinct()
        for i in commonly_liked_artists_tracks:
            data.append(Track.objects.get(id=i))

    return data
