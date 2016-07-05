from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import RequestLog


@receiver(post_save, sender=RequestLog)
def submit_to_piwik(sender, instance, created, *args, **kwargs):
    """
    All API requests must be logged to Piwik for statistical purposes (single application for all stats).
    """
    if created:
        instance.submit_to_piwik()