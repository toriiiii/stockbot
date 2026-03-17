from django.contrib.auth.models import AbstractUser
from django.db import models

class StockBotUser(AbstractUser):
    botID = models.IntegerField(default=0, unique=True)

    def __str__(self):
        return self.username
    
class DeviceToken(models.Model):
    """
    Stores each user's Expo push token so Django can send
    push notifications to their device.
    """
    user = models.ForeignKey(
        StockBotUser,
        on_delete=models.CASCADE,
        related_name='device_tokens',
    )
    token = models.TextField(unique=True)  # ExponentPushToken[...]
    platform = models.CharField(
        max_length=10,
        choices=[('ios', 'iOS'), ('android', 'Android')],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} — {self.platform}'