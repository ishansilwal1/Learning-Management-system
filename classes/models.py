from django.db import models
from users.models import CustomUser

class ClassRoom(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100, default='General')  # <-- Add default value here
    description = models.TextField(blank=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owned_classes')
    sub_owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_owned_classes')
    invite_code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # slug field removed

    def __str__(self):
        return self.name

class ClassMembership(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('sub_owner', 'Sub-owner'),
        ('participant', 'Participant'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'classroom')

    def __str__(self):
        return f"{self.user.username} in {self.classroom.name} as {self.role}"
