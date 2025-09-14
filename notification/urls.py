from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('mark-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('unread-count/', views.get_unread_count, name='get_unread_count'),
]