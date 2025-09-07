from django.shortcuts import render, redirect
from .models import Post
from classes.models import ClassRoom
from django.contrib.auth.decorators import login_required

@login_required
def post_announcement(request, class_id):
    classroom = ClassRoom.objects.get(id=class_id)
    if request.method == 'POST' and request.POST.get('announcement'):
        content = request.POST['announcement']
        Post.objects.create(
            classroom=classroom,
            author=request.user,
            content=content
        )
        return redirect('class_detail', class_id=class_id)
    return redirect('class_detail', class_id=class_id)

@login_required
def list_announcements(request, class_id):
    classroom = ClassRoom.objects.get(id=class_id)
    posts = Post.objects.filter(classroom=classroom).order_by('-created_at')
    return render(request, 'community/announcement_list.html', {'posts': posts, 'classroom': classroom})
