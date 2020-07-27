from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import SocialUser


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    print("TEST")
    user = instance
    if created:
        SocialUser.objects.create(user=user)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
