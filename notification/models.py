from django.db import models
from users.models import CustomUser
from classes.models import ClassRoom, ClassMembership
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('assignment', 'New Assignment'),
        ('announcement', 'New Announcement'),
        ('material', 'New Material'),
    ]
    
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, null=True, blank=True)
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='announcement')
    title = models.CharField(max_length=255, default='')
    message = models.TextField(default='')
    
    # Generic foreign key to link to different content types (Assignment, Post, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"To {self.recipient.username}: {self.title}"

    @staticmethod
    def create_notifications_for_class(classroom, sender, notification_type, title, message, content_object=None):
        """
        Create notifications for all members of a class
        """
        # Get all class members except the sender
        members = ClassMembership.objects.filter(classroom=classroom).exclude(user=sender)
        
        notifications = []
        for membership in members:
            notification = Notification(
                recipient=membership.user,
                sender=sender,
                classroom=classroom,
                notification_type=notification_type,
                title=title,
                message=message,
                content_object=content_object
            )
            notifications.append(notification)
        
        # Bulk create for efficiency
        Notification.objects.bulk_create(notifications)
        return len(notifications)