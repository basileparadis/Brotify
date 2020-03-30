from django.contrib.auth.decorators import login_required
from django.db import models

# Create your models here.
from django.contrib.auth.models import User


@login_required
def liste_amis():
    return User.objects.all()

