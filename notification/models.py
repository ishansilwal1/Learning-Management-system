from django.db import models
from users.models import CustomUser

class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"To {self.recipient.username}: {self.message[:30]}"