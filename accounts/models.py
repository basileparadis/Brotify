from django.contrib.auth.models import User
from django.db import models

'''
# Create your models here.
class UserProfile(models.Model):
    # username = models.OneToOneField(User, on_delete=models.CASCADE)
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    user = models.OneToOneField(User, related_name='user_data', on_delete=models.CASCADE)
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    courriel = models.EmailField('courriel', unique=True)
    username = User.username
    USERNAME_FIELD = 'username'
    avatar = models.ImageField(upload_to="media", null=True, blank=True)
    description = models.TextField(max_length=2000, default='', null=True, blank=True)
'''


class SocialUser(models.Model):
    user = models.OneToOneField(User, related_name='user_info', on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='media', null=True, blank=True, verbose_name='Mon avatar')
    description = models.TextField(max_length=2000, default='', null=True, blank=True)

    def __str__(self):
        return self.avatar.url
