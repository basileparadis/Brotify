from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# from django.shortcuts import render
from django.contrib.auth.models import User
from django.template import loader
from friendship.models import Friend, FriendshipRequest
from accounts.models import SocialUser


@login_required
def index(request):
    liste_amis_id = []
    list_sent_invitation_id = []
    list_received_invitation_id = []

    users = User.objects.all()
    social_user = SocialUser.objects.all().order_by('-id')

    # On vérifie les liens d'amitié entre un utilisateur
    friends = Friend.objects.all()
    for friend in friends:
        if request.user.id is friend.to_user_id:
            liste_amis_id.append(friend.from_user_id)
        elif request.user.id is friend.from_user_id:
            liste_amis_id.append(friend.to_user_id)

    # On vérifie les invitations envoyées d'un utilisateur
    invitations = FriendshipRequest.objects.all()
    for invitation in invitations:
        if request.user.id is invitation.from_user_id:
            list_sent_invitation_id.append(invitation.to_user_id)

    # On vérifie les invitations reçus d'un utilisateur
    invitations = FriendshipRequest.objects.all()
    for invitation in invitations:
        if request.user.id is invitation.to_user_id:
            list_received_invitation_id.append(invitation.from_user_id)

    template = loader.get_template('friends.html')
    context = {
        'users': users,
        'social': social_user,
        'id_amis': liste_amis_id,
        'id_invitation_sent': list_sent_invitation_id,
        'id_invitation_received': list_received_invitation_id,
    }
    return HttpResponse(template.render(context, request))


@login_required
def accepter_amitie(request, otherUser):
    try:
        friend_request = FriendshipRequest.objects.get(from_user=request.user.id, to_user=otherUser.id)
        friend_request.reject()
    except Friend.DoesNotExist as exception:
        print("La demande d'amitié est introuvable")
        print(exception)


@login_required
def refuser_amitie(request, otherUser):
    try:
        friend_request = FriendshipRequest.objects.get(from_user=request.user.id, to_user=otherUser.id)
        friend_request.accept()
    except Friend.DoesNotExist as exception:
        print("La demande d'amitié est introuvable")
        print(exception)
