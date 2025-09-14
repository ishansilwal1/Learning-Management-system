from django.urls import path
from . import views

urlpatterns = [
    path('upload_material/<int:class_id>/', views.upload_material, name='upload_material'),
]