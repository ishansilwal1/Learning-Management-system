from django.contrib import admin
from .models import Grade

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('classroom', 'student', 'marked_by', 'marks_obtained', 'total_marks', 'graded_at')
    search_fields = ()
