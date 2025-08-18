from django.urls import path
from .views import user_login, dashboard, register, verify_email, user_logout

urlpatterns = [
    path('login/', user_login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('register/', register, name='register'),
    path('verify-email/<int:uid>/<str:token>/', verify_email, name='verify_email'),
    path('logout/', user_logout, name='logout'),
]