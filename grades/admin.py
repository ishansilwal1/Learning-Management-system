from django.contrib import admin
from .models import Grade

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'grade', 'get_percentage', 'is_passed', 'marked_by', 'graded_at')
    list_filter = ('grade', 'is_passed', 'graded_at', 'assignment__classroom')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'assignment__title')
    readonly_fields = ('grade', 'is_passed', 'graded_at', 'updated_at')
    ordering = ('-graded_at',)
    
    fieldsets = (
        (None, {
            'fields': ('student', 'assignment', 'classroom', 'marks_obtained', 'total_marks')
        }),
        ('Grade Information', {
            'fields': ('grade', 'is_passed', 'remarks'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('marked_by', 'graded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('student', 'assignment', 'marked_by', 'classroom')
    
    def get_percentage(self, obj):
        return f"{obj.get_percentage()}%"
    get_percentage.short_description = 'Percentage'
    
    def save_model(self, request, obj, form, change):
        if not change:  # New grade
            obj.marked_by = request.user
        super().save_model(request, obj, form, change)
