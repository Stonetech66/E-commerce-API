from django.dispatch import receiver
from .models import MyUser, UserProfile
from django.db.models.signals import post_save


@receiver(post_save, sender=MyUser)
def create_userprofile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    
@receiver(post_save, sender=MyUser)
def save_userprofile(sender, instance, created, **kwargs):
    instance.user_profile.save()
