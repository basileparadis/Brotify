from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.template import loader
from friendship.models import Friend, Follow, Block

# Create your views here.
from accounts.models import SocialUser


@login_required
def index(request):
    liste_amis = []
    users = User.objects.all()
    social_user = SocialUser.objects.all().order_by('-id')
    friends = Friend.objects.all().filter(id=request.user.id)
    for friend in friends:
        liste_amis.append(friend.to_user_id)
    print(Friend.objects.all().filter(id__exact=request.user.id))
    template = loader.get_template('friends.html')
    context = {
        'users': users,
        'social': social_user,
        'amis': liste_amis,
    }
    return HttpResponse(template.render(context, request))
