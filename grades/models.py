from django.db import models
from classes.models import ClassRoom
from users.models import CustomUser
from assignments.models import Assignment

class Grade(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+ (90-100)'),
        ('A', 'A (80-89)'),
        ('B+', 'B+ (70-79)'),
        ('B', 'B (60-69)'),
        ('C+', 'C+ (50-59)'),
        ('C', 'C (40-49)'),
        ('D', 'D (30-39)'),
        ('F', 'F (0-29)'),
    ]
    
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'normal'})
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True, blank=True)
    marked_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='marked_grades')
    
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True)
    is_passed = models.BooleanField(default=False)
    
    remarks = models.TextField(blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['classroom', 'student', 'assignment']
        ordering = ['-graded_at']

    def save(self, *args, **kwargs):
        # Auto-calculate grade and pass/fail status
        percentage = (self.marks_obtained / self.total_marks) * 100
        
        if percentage >= 90:
            self.grade = 'A+'
        elif percentage >= 80:
            self.grade = 'A'
        elif percentage >= 70:
            self.grade = 'B+'
        elif percentage >= 60:
            self.grade = 'B'
        elif percentage >= 50:
            self.grade = 'C+'
        elif percentage >= 40:
            self.grade = 'C'
        elif percentage >= 30:
            self.grade = 'D'
        else:
            self.grade = 'F'
            
        self.is_passed = percentage >= 40  # 40% is passing grade
        super().save(*args, **kwargs)

    def get_percentage(self):
        return round((self.marks_obtained / self.total_marks) * 100, 2)

    def __str__(self):
        assignment_name = f" - {self.assignment.title}" if self.assignment else ""
        return f"{self.student.username} - {self.classroom.name}{assignment_name}: {self.grade} ({self.get_percentage()}%)"
