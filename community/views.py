from django.shortcuts import render, redirect
from .models import Post
from classes.models import ClassRoom
from django.contrib.auth.decorators import login_required
from notification.models import Notification

@login_required
def post_announcement(request, class_id):
    classroom = ClassRoom.objects.get(id=class_id)
    if request.method == 'POST' and request.POST.get('announcement'):
        content = request.POST['announcement']
        post = Post.objects.create(
            classroom=classroom,
            author=request.user,
            content=content
        )
        
        # Send notifications to all class members
        notification_title = f"New Announcement in {classroom.name}"
        notification_message = f"A new announcement has been posted: {content[:100]}{'...' if len(content) > 100 else ''}"
        
        Notification.create_notifications_for_class(
            classroom=classroom,
            sender=request.user,
            notification_type='announcement',
            title=notification_title,
            message=notification_message,
            content_object=post
        )
        
        return redirect('class_detail', class_id=class_id)
    return redirect('class_detail', class_id=class_id)

@login_required
def list_announcements(request, class_id):
    classroom = ClassRoom.objects.get(id=class_id)
    posts = Post.objects.filter(classroom=classroom).order_by('-created_at')
    return render(request, 'community/announcement_list.html', {'posts': posts, 'classroom': classroom})
