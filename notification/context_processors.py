from .models import Notification

def notification_context(request):
    """Add unread notification count to template context"""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user, 
            read=False
        ).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}