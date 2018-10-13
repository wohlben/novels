from .models import Scrapes
from django.dispatch import receiver
from django.db.models.signals import post_save


# @receiver(post_save, sender=Scrapes)
# def watchScrapes(sender, instance, created, **kwargs):
#     if created:
#         fetchUrl.delay(instance.id)
