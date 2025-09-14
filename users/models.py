"""User model extensions."""
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """Extended user model with user types and profile image."""
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('normal', 'Normal User'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='normal')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"