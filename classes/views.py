from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ClassRoom, ClassMembership
from django.contrib.auth.decorators import login_required
import uuid

@login_required
def create_class(request):
    if request.method == 'POST':
        name = request.POST.get('class_name')
        subject = request.POST.get('subject')
        description = request.POST.get('description', '')
        invite_code = uuid.uuid4().hex[:8].upper()

        classroom = ClassRoom.objects.create(
            name=name,
            subject=subject,
            description=description,
            owner=request.user,
            invite_code=invite_code
        )
        request.session['invite_code'] = invite_code
        return redirect('dashboard')

    return render(request, 'classes/create_class.html')

@login_required
def join_class(request):
    if request.method == 'POST':
        invite_code = request.POST.get('invite_code')
        try:
            classroom = ClassRoom.objects.get(invite_code=invite_code)
            if classroom.owner == request.user or ClassMembership.objects.filter(user=request.user, classroom=classroom).exists():
                messages.info(request, "You are already a member of this class.")
            else:
                ClassMembership.objects.create(user=request.user, classroom=classroom)
                messages.success(request, f"You have joined {classroom.name}!")
        except ClassRoom.DoesNotExist:
            messages.error(request, "Invalid invitation code.")
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def class_detail(request, class_id):
    classroom = get_object_or_404(ClassRoom, id=class_id)
    return render(request, 'classes/class_detail.html', {'classroom': classroom})
