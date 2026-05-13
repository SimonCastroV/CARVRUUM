from django.db.models.signals import post_save
from django.dispatch import receiver

from messaging.models import Message
from .models import Notification


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):

    if not created:
        return

    conversation = instance.conversation

    # Detectar receptor
    if instance.sender == conversation.buyer:
        recipient = conversation.seller
    else:
        recipient = conversation.buyer

    # Evitar notificarse a sí mismo
    if recipient == instance.sender:
        return

    Notification.objects.create(
        recipient=recipient,
        sender=instance.sender,
        title=f"te envió un mensaje|{conversation.pk}"
    )