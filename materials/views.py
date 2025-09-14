from django.shortcuts import render, redirect
from .models import Material
from classes.models import ClassRoom
from django.contrib.auth.decorators import login_required
from notification.models import Notification

@login_required
def upload_material(request, class_id):
    classroom = ClassRoom.objects.get(id=class_id)
    if request.method == 'POST' and request.FILES.get('material'):
        title = request.POST.get('title', 'Material')
        file = request.FILES['material']
        material = Material.objects.create(
            classroom=classroom,
            uploaded_by=request.user,
            title=title,
            file=file
        )
        
        # Send notifications to all class members
        notification_title = f"New Material: {title}"
        notification_message = f"A new material '{title}' has been uploaded to {classroom.name}"
        
        Notification.create_notifications_for_class(
            classroom=classroom,
            sender=request.user,
            notification_type='material',
            title=notification_title,
            message=notification_message,
            content_object=material
        )
        
        return redirect('class_detail', class_id=class_id)
    return redirect('class_detail', class_id=class_id)

@login_required
def list_materials(request, class_id):
    classroom = ClassRoom.objects.get(id=class_id)
    materials = Material.objects.filter(classroom=classroom)
    return render(request, 'materials/material_list.html', {'materials': materials, 'classroom': classroom})
