from django.urls import path
from . import views

urlpatterns = [
    path('', views.assignment, name='assignment'),
    path('create/', views.create_assignment, name='create_assignment'),
    path('<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
]