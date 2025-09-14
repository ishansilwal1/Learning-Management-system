from django.urls import path
from . import views

app_name = 'grades'

urlpatterns = [
    path('manage/<int:class_id>/', views.manage_grades, name='manage_grades'),
    path('assign/<int:class_id>/<int:assignment_id>/', views.assign_grade, name='assign_grade'),
    path('my-grades/', views.student_grades, name='student_grades'),
    path('summary/<int:class_id>/', views.class_grades_summary, name='class_summary'),
]