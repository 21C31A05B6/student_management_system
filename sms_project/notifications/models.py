from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Logs every email/SMS sent by the system (Modules: Email & SMS Notifications).
    Even when no real SMS gateway is configured, every message is recorded here
    so the feature is fully visible/testable."""

    class Channel(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS = 'SMS', 'SMS'
        WHATSAPP = 'WHATSAPP', 'WhatsApp'

    class Status(models.TextChoices):
        SENT = 'SENT', 'Sent'
        FAILED = 'FAILED', 'Failed'

    recipient_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='notifications')
    channel = models.CharField(max_length=10, choices=Channel.choices)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SENT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.channel}] to {self.recipient_user} - {self.status}"
