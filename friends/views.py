from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse
# from django.shortcuts import render
from django.contrib.auth.models import User
from django.template import loader
from friendship.models import Friend, FriendshipRequest
from accounts.models import SocialUser
from biblio.models import Biblio, Track


@login_required
def index(request):
    users = User.objects.all()
    social_user = SocialUser.objects.all().order_by('-id')
    template = loader.get_template('friends.html')
    liste_chansons_comparees = None

    # print(request.POST)
    if 'accept_friend' in request.POST:
        accepter_amitie(request)
    elif 'deny-friend' in request.POST:
        refuser_amitie(request)
    elif 'add-friend' in request.POST:
        ajouter_amitie(request)
    elif 'remove-friend' in request.POST:
        retirer_amitie(request)
    elif 'compare' in request.POST:
        liste_chansons_comparees = compare(request)

    context = {
        'users': users,
        'social': social_user,
        'current_user': request.user,
        'id_amis': get_friends(request),
        'id_invitation_sent': get_sent_friend_request(request),
        'id_invitation_received': get_received_friend_request(request),
        'chansons_comparees': liste_chansons_comparees,
    }
    return HttpResponse(template.render(context, request))


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


# On vérifie les invitations reçus d'un utilisateur
@login_required()
def get_received_friend_request(request):
    list_received_invitation_id = []
    invitations = FriendshipRequest.objects.all()
    for invitation in invitations:
        if request.user.id is invitation.to_user_id:
            list_received_invitation_id.append(invitation.from_user_id)
    return list_received_invitation_id


@login_required
def accepter_amitie(request):
    ami_potentiel_id = int(request.POST.get('accept_friend'))
    print(ami_potentiel_id)
    print(request.user.id)
    try:
        friend_request = FriendshipRequest.objects.get(from_user=ami_potentiel_id, to_user=request.user.id)
        friend_request.accept()
    except FriendshipRequest.DoesNotExist as exception:
        print("La demande d'amitié est introuvable")
        print(exception)
    except FriendshipRequest.AlreadyFriendsError as exception:
        print("Vous êtes déjà amis")
        print(exception)


@login_required
def refuser_amitie(request):
    ami_potentiel_id = request.POST.get('deny-friend')
    try:
        friend_request = FriendshipRequest.objects.get(from_user=request.user.id, to_user=ami_potentiel_id)
        friend_request.reject()
    except FriendshipRequest.DoesNotExist as exception:
        print("La demande d'amitié est introuvable")
        print(exception)


@login_required
def retirer_amitie(request):
    personne_id = request.POST.get('remove-friend')
    try:
        Friend.objects.remove_friend(request.user, User.objects.get(id=personne_id))
    except User.DoesNotExist as exception:
        print("L'utilisateur est introuvable")
        print(exception)


@login_required
def ajouter_amitie(request):
    personne_id = request.POST.get('add-friend')
    try:
        Friend.objects.add_friend(request.user, User.objects.get(id=personne_id))
        print('done')
    except User.DoesNotExist as exception:
        print("L'utilisateur est introuvable")
        print(exception)
    except IntegrityError as exception:
        print("La demande a déjà été créée")
        print(exception)


@login_required
def compare(request):
    # Définir les usagers
    usager = request.user
    ami = User.objects.get(id=request.POST.get('compare'))
    # Obtenir une liste des id des chansons d'un utilisateur (biblio)
    liste_biblio_usager = Biblio.objects.filter(user=usager).values_list('user_song_id', flat=True)
    liste_biblio_ami = Biblio.objects.filter(user=ami).values_list('user_song_id', flat=True)
    # Obtenir les chansons dont le id est présent dans les deux biblios
    tracks = Track.objects.filter(Q(id__in=liste_biblio_usager), Q(id__in=liste_biblio_ami))
    '''
    liste_commun = Biblio.objects.filter(
        Q(user_song_id__in=my_tracks),
        Q(user_song_id__in=friend_tracks)
    )
    # liste_commun = Biblio.objects.filter(user_id=request.user.id)
    print('COMMUN')
    for biblio in liste_commun:
        print(Track.objects.get(id=biblio.user_song_id).title)
    '''
    return tracks
