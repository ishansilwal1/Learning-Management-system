from django.urls import path
from .import views

urlpatterns = [
    path('', views.user_login, name='home'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('verify-email/<int:uid>/<str:token>/', views.verify_email, name='verify_email'),
    path('logout/', views.user_logout, name='logout'),]