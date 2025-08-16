from django.contrib import admin
from .models import ClassRoom, ClassMembership

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'sub_owner', 'invite_code', 'created_at')
    search_fields = ('name', 'owner__username', 'sub_owner__username', 'invite_code')

@admin.register(ClassMembership)
class ClassMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'classroom', 'role', 'joined_at')
    search_fields = ('user__username', 'classroom__name','role')