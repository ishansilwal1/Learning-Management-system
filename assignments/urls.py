from django.urls import path
from . import views

urlpatterns = [
    path('', views.assignment, name='assignment'),
    path('class/<int:class_id>/', views.class_assignments, name='class_assignments'),
    path('calendar/', views.assignment_calendar, name='assignment_calendar'),
    path('create/', views.create_assignment, name='create_assignment'),
    path('<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
]