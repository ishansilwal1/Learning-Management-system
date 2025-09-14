from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Notification

@login_required
def notification_list(request):
    """Display all notifications for the current user"""
    notifications = Notification.objects.filter(recipient=request.user)
    unread_count = notifications.filter(read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notification/notification_list.html', context)

@login_required
def mark_as_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Notification marked as read.')
    return redirect('notification_list')

@login_required
def mark_all_as_read(request):
    """Mark all notifications as read for the current user"""
    if request.method == 'POST':
        updated_count = Notification.objects.filter(
            recipient=request.user, 
            read=False
        ).update(read=True)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'count': updated_count})
        
        messages.success(request, f'{updated_count} notifications marked as read.')
    
    return redirect('notification_list')

@login_required
def get_unread_count(request):
    """AJAX endpoint to get unread notification count"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        count = Notification.objects.filter(recipient=request.user, read=False).count()
        return JsonResponse({'unread_count': count})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
