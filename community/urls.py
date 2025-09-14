from django.urls import path
from . import views

urlpatterns = [
    path('post_announcement/<int:class_id>/', views.post_announcement, name='post_announcement'),
]