from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_class, name='create_class'),
    path('<int:class_id>/', views.class_detail, name='class_detail')
]