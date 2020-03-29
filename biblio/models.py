from django.db import models

# Create your models here.
from django.contrib.auth.models import User
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    # user = User.objects.get(...)
    #user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    #gender = models.CharField(max_length=20)
    savedTracks = {}
    savedAlbums = {}
    followedArtists = {}
    #social = user.social_auth.get(provider='spotify-oauth2')
    #response = requests.get(
    #    'https://api.spotify.com/v1/me/tracks',
    #    params={'access_token': social.extra_data['access_token']}
    #)
    #friends = response.json()['items']
    '''

    print("Les chansons " + friends)



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    '''