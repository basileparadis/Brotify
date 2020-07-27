import os

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default_user_pic.webp',
                               null=True,
                               blank=True,
                               upload_to='profile_pic',
                               verbose_name='Avatar')
    avatar_thumbnail = ImageSpecField(source='avatar',
                                      processors=[ResizeToFill(50, 50)],
                                      format='JPEG',
                                      options={'quality': 100})
    description = models.TextField(max_length=2000,
                                   default='',
                                   null=True,
                                   blank=True)

# These two auto-delete files from filesystem when they are unneeded:


@receiver(models.signals.post_delete, sender=SocialUser)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)


@receiver(models.signals.pre_save, sender=SocialUser)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = SocialUser.objects.get(pk=instance.pk).avatar
    except SocialUser.DoesNotExist:
        return False

    new_file = instance.avatar
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
