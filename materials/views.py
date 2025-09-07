from django.shortcuts import render, redirect
from .models import Material
from classes.models import ClassRoom
from django.contrib.auth.decorators import login_required

@login_required
def upload_material(request, class_id):
    classroom = ClassRoom.objects.get(id=class_id)
    if request.method == 'POST' and request.FILES.get('material'):
        title = request.POST.get('title', 'Material')
        file = request.FILES['material']
        Material.objects.create(
            classroom=classroom,
            uploaded_by=request.user,
            title=title,
            file=file
        )
        return redirect('class_detail', class_id=class_id)
    return redirect('class_detail', class_id=class_id)

@login_required
def list_materials(request, class_id):
    classroom = ClassRoom.objects.get(id=class_id)
    materials = Material.objects.filter(classroom=classroom)
    return render(request, 'materials/material_list.html', {'materials': materials, 'classroom': classroom})
