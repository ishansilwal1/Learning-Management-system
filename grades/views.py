from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q
from classes.models import ClassRoom
from assignments.models import Assignment, Submission
from .models import Grade
from django.http import JsonResponse

@login_required
def manage_grades(request, class_id):
    """View for class owners to manage grades for assignments"""
    classroom = get_object_or_404(ClassRoom, id=class_id)
    
    # Check if user is the class owner
    if request.user != classroom.owner:
        messages.error(request, "You don't have permission to manage grades for this class.")
        return redirect('class_detail', class_id=class_id)
    
    # Get all assignments for this class
    assignments = Assignment.objects.filter(classroom=classroom).order_by('-created_at')
    
    # Get selected assignment for grading
    selected_assignment_id = request.GET.get('assignment_id')
    selected_assignment = None
    submissions = None
    
    if selected_assignment_id:
        selected_assignment = get_object_or_404(Assignment, id=selected_assignment_id, classroom=classroom)
        # Get submissions for the selected assignment
        submissions = Submission.objects.filter(assignment=selected_assignment).select_related('student').order_by('student__username')
        
        # Add grade information to submissions
        for submission in submissions:
            try:
                submission.grade = Grade.objects.get(student=submission.student, assignment=selected_assignment)
            except Grade.DoesNotExist:
                submission.grade = None
    
    context = {
        'classroom': classroom,
        'assignments': assignments,
        'selected_assignment': selected_assignment,
        'submissions': submissions,
    }
    
    return render(request, 'grades/manage_grades.html', context)

@login_required
def assign_grade(request, class_id, assignment_id):
    """AJAX view to assign grade to a student"""
    if request.method == 'POST':
        classroom = get_object_or_404(ClassRoom, id=class_id)
        assignment = get_object_or_404(Assignment, id=assignment_id, classroom=classroom)
        
        # Check if user is the class owner
        if request.user != classroom.owner:
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        
        student_id = request.POST.get('student_id')
        marks_obtained = request.POST.get('percentage')
        
        try:
            marks_obtained = float(marks_obtained)
            if marks_obtained < 0 or marks_obtained > 100:
                return JsonResponse({'success': False, 'error': 'Marks must be between 0 and 100'})
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid marks value'})
        
        # Create or update grade
        grade, created = Grade.objects.get_or_create(
            student_id=student_id,
            assignment=assignment,
            classroom=classroom,
            defaults={
                'marks_obtained': marks_obtained, 
                'total_marks': 100,
                'marked_by': request.user
            }
        )
        
        if not created:
            grade.marks_obtained = marks_obtained
            grade.total_marks = 100
            grade.marked_by = request.user
            grade.save()
        
        return JsonResponse({
            'success': True,
            'letter_grade': grade.grade,
            'passed': grade.is_passed,
            'created': created
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
def student_grades(request):
    """View for students to see their grades"""
    # Get all grades for the current student
    grades = Grade.objects.filter(student=request.user).select_related(
        'assignment', 'assignment__classroom', 'marked_by'
    ).order_by('-graded_at')
    
    # Pagination
    paginator = Paginator(grades, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics
    total_grades = grades.count()
    passed_grades = grades.filter(is_passed=True).count()
    average_percentage = 0
    if total_grades > 0:
        total_percentage = sum([grade.get_percentage() for grade in grades])
        average_percentage = round(total_percentage / total_grades, 2)
    
    # Get grade distribution
    grade_distribution = {}
    for grade in grades:
        letter = grade.grade
        grade_distribution[letter] = grade_distribution.get(letter, 0) + 1
    
    # ML Analytics - Get analytics for each classroom
    ml_analytics = {}
    try:
        from ml.predictions import get_student_analytics
        from classes.models import ClassMembership
        
        # Get all classrooms where student is enrolled
        memberships = ClassMembership.objects.filter(user=request.user, role='participant')
        
        for membership in memberships:
            try:
                analytics = get_student_analytics(request.user, membership.classroom)
                ml_analytics[membership.classroom.id] = analytics
            except Exception as e:
                print(f"ML Analytics error for {membership.classroom.name}: {e}")
                ml_analytics[membership.classroom.id] = {
                    'error': 'Analytics unavailable',
                    'performance_trend': 'Unknown'
                }
    except Exception as e:
        print(f"ML Analytics module error: {e}")
        ml_analytics = {}
    
    context = {
        'page_obj': page_obj,
        'total_grades': total_grades,
        'passed_grades': passed_grades,
        'failed_grades': total_grades - passed_grades,
        'pass_rate': (passed_grades / total_grades * 100) if total_grades > 0 else 0,
        'average_percentage': average_percentage,
        'grade_distribution': grade_distribution,
        'ml_analytics': ml_analytics,
    }
    
    return render(request, 'grades/student_grades.html', context)

@login_required
def class_grades_summary(request, class_id):
    """View for class owners to see overall grade summary"""
    classroom = get_object_or_404(ClassRoom, id=class_id)
    
    # Check if user is the class owner
    if request.user != classroom.owner:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('class_detail', class_id=class_id)
    
    # Get all grades for assignments in this class
    grades = Grade.objects.filter(classroom=classroom).select_related(
        'student', 'assignment', 'marked_by'
    ).order_by('-graded_at')
    
    # Get assignments for this class
    assignments = Assignment.objects.filter(classroom=classroom).order_by('-created_at')
    
    # Add submission and grade counts manually
    for assignment in assignments:
        assignment.total_submissions = assignment.submissions.count()
        assignment.total_grades = Grade.objects.filter(assignment=assignment).count()
    
    # Calculate class statistics
    total_students = classroom.classmembership_set.filter(role='participant').count()
    total_grades = grades.count()
    passed_grades = grades.filter(is_passed=True).count()
    average_percentage = 0
    if total_grades > 0:
        total_percentage = sum([grade.get_percentage() for grade in grades])
        average_percentage = round(total_percentage / total_grades, 2)
    
    # Grade distribution for the class
    grade_distribution = {}
    for grade in grades:
        letter = grade.grade
        grade_distribution[letter] = grade_distribution.get(letter, 0) + 1
    
    context = {
        'classroom': classroom,
        'assignments': assignments,
        'total_students': total_students,
        'total_grades': total_grades,
        'passed_grades': passed_grades,
        'failed_grades': total_grades - passed_grades,
        'pass_rate': (passed_grades / total_grades * 100) if total_grades > 0 else 0,
        'average_percentage': average_percentage,
        'grade_distribution': grade_distribution,
        'recent_grades': grades[:10],  # Last 10 grades
    }
    
    return render(request, 'grades/class_summary.html', context)
