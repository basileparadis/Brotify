from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.template import loader
from accounts.models import SocialUser
import friends.models as amitie


@login_required
def index(request):
    users = User.objects.all()
    social_user = SocialUser.objects.all().order_by('-id')
    template = loader.get_template('friends.html')
    liste_chansons_comparees = None

    # print(request.POST)
    if 'accept_friend' in request.POST:
        amitie.accepter_amitie(request)
    elif 'deny-friend' in request.POST:
        amitie.refuser_amitie(request)
    elif 'add-friend' in request.POST:
        amitie.ajouter_amitie(request)
    elif 'remove-friend' in request.POST:
        amitie.retirer_amitie(request)
    elif 'compare' in request.POST:
        liste_chansons_comparees = amitie.compare(request)

    context = {
        'users': users,
        'social': social_user,
        'current_user': request.user,
        'id_amis': amitie.get_friends(request),
        'id_invitation_sent': amitie.get_sent_friend_request(request),
        'id_invitation_received': amitie.get_received_friend_request(request),
        'chansons_comparees': liste_chansons_comparees,
    }
    return HttpResponse(template.render(context, request))


