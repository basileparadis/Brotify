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
    users = User.objects.all()
    social_user = SocialUser.objects.all().order_by('-id')
    template = loader.get_template('friends.html')
    context = {
        'users': users,
        'social': social_user,
    }
    return HttpResponse(template.render(context, request))
