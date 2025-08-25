from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_class, name='create_class'),
]