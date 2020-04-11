from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.template import loader
from friendship.models import Friend, Follow, Block

# Create your views here.
from accounts.models import UserProfile


@login_required
def index(request):
    users = User.objects.all()
    avatar = UserProfile.avatar
    template = loader.get_template('friends.html')
    context = {
        'users': users,
        'avatar': avatar,
    }
    return HttpResponse(template.render(context, request))
