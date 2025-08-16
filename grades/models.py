from django.db import models
from classes.models import ClassRoom
from users.models import CustomUser

class Grade(models.Model):
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'normal'})
    marked_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='marked_grades')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.CharField(max_length=255, blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.classroom.name}: {self.marks_obtained}/{self.total_marks}"
