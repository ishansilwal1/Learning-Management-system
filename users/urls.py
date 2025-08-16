from django.urls import path
from .views import user_login,dashboard,register

urlpatterns = [
    path('login/', user_login, name='login'),
     path('dashboard/',dashboard, name='check'),
    path('register/', register, name='register'),
]