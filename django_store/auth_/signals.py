from django.db.models.signals import post_save
from django.dispatch import receiver
from auth_.models import User, Profile
import logging
logger= logging.getLogger('authorization')


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        logger.info(f"User : {instance.username} created")
        Profile.objects.create(user=instance)