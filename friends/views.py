import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.core import serializers
from django.template import loader
from accounts.models import SocialUser
import friends.models as amitie


@login_required
def index(request):
    template = loader.get_template('friends.html')

    users = User.objects.all()
    social_user = SocialUser.objects.all().order_by('-id')

    if request.POST.get('action_type') == "accept_friend":
        amitie.accepter_amitie(request)
    elif request.POST.get('action_type') == 'deny-friend':
        amitie.refuser_amitie(request)
    elif request.POST.get('action_type') == 'add-friend':
        amitie.add_friendship(request)
    elif request.POST.get('action_type') == 'remove-friend':
        amitie.retirer_amitie(request)
    elif request.POST.get('action_type') == 'compare_tracks':
        compare_tracks(request)

    context = {
        'users': users,
        'social': social_user,
        'current_user': request.user,
        'id_amis': amitie.get_friends(request),
        'id_invitation_sent': amitie.get_sent_friend_request(request),
        'id_invitation_received': amitie.get_received_friend_request(request),
    }

    return HttpResponse(template.render(context, request))


@login_required
def compare(request, friend_username):
    # friend = User.objects.get(username=friend_username)
    template = loader.get_template('results.html')
    '''
    list_of_tracks_in_common = amitie.compare_songs(request, friend)
    graph_compared_artists_json = amitie.compare_artists(request, friend)
    list_suggested_songs = amitie.get_suggested_tracks(request, friend)

    context = {
        'tracks_in_common': list_of_tracks_in_common,
        'compared_artists': graph_compared_artists_json,
        'suggested_songs': list_suggested_songs,
    }
    '''
    return HttpResponse(template.render(None, request))


@login_required
def compare_tracks(request, friend_username):
    # friend_id = request.POST.get('user')
    template = loader.get_template('song_list.html')
    friend = User.objects.get(username=friend_username)
    list_of_tracks_in_common = amitie.compare_songs(request, friend)

    context = {
        'tracks_in_common': list_of_tracks_in_common,
    }
    # return JsonResponse(qr_json, safe=False)
    return HttpResponse(template.render(context, request))


@login_required
def compare_artists(request, friend_username):
    friend = User.objects.get(username=friend_username)
    graph_compared_artists_json = amitie.compare_artists(request, friend)

    return JsonResponse(graph_compared_artists_json, safe=False)
