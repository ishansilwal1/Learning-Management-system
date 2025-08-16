from django.contrib import admin
from .models import Material

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'classroom', 'uploaded_by', 'uploaded_at')
    search_fields = ('title', 'classroom__name', 'uploaded_by__username')

# Register your models here.
