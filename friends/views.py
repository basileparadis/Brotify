from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
from friendship.models import Friend, Follow, Block


# Create your views here.

@login_required
def index(request):
    users = list(User.objects.values("username"))
    return render(request, 'friends.html', {"users": users})
