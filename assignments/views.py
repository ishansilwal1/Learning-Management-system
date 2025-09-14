from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
import json
from datetime import datetime, timedelta
import calendar
from .models import Assignment, Submission
from classes.models import ClassRoom, ClassMembership
from notification.models import Notification

@login_required
def assignment(request):
    """Display all assignments for the user's classes."""
    owned_classes = ClassRoom.objects.filter(owner=request.user)
    
    joined_memberships = ClassMembership.objects.filter(user=request.user)
    joined_classes = ClassRoom.objects.filter(id__in=joined_memberships.values_list('classroom_id', flat=True))
    
    all_user_classes = (owned_classes | joined_classes).distinct()
    assignments = Assignment.objects.filter(classroom__in=all_user_classes).order_by('-created_at')
    
    for assignment in assignments:
        assignment.is_overdue = timezone.now() > assignment.deadline
        assignment.is_owner = assignment.classroom.owner == request.user
        
        if not assignment.is_owner:
            try:
                assignment.user_submission = Submission.objects.get(
                    assignment=assignment, 
                    student=request.user
                )
            except Submission.DoesNotExist:
                assignment.user_submission = None
    
    context = {
        'assignments': assignments,
        'owned_classes': owned_classes,
        'show_all': True,
    }
    return render(request, 'assignments/assignment.html', context)

@login_required
def class_assignments(request, class_id):
    """View assignments for a specific class."""
    classroom = get_object_or_404(ClassRoom, id=class_id)
    
    is_owner = classroom.owner == request.user
    is_member = ClassMembership.objects.filter(user=request.user, classroom=classroom).exists()
    
    if not (is_owner or is_member):
        messages.error(request, "You don't have access to this class.")
        return redirect('dashboard')
    
    assignments = Assignment.objects.filter(classroom=classroom).order_by('-created_at')
    
    # Add submission status for each assignment
    for assignment in assignments:
        assignment.is_overdue = timezone.now() > assignment.deadline
        assignment.is_owner = assignment.classroom.owner == request.user
        
        if not assignment.is_owner:
            try:
                assignment.user_submission = Submission.objects.get(
                    assignment=assignment, 
                    student=request.user
                )
            except Submission.DoesNotExist:
                assignment.user_submission = None
    
    context = {
        'assignments': assignments,
        'classroom': classroom,
        'show_all': False,  # Flag to indicate this shows class-specific assignments
    }
    return render(request, 'assignments/assignment.html', context)

@login_required
def create_assignment(request):
    # Get the class_id from URL parameter if provided (for class-specific creation)
    class_id = request.GET.get('class_id')
    selected_classroom = None
    
    if class_id:
        try:
            selected_classroom = ClassRoom.objects.get(id=class_id, owner=request.user)
        except ClassRoom.DoesNotExist:
            messages.error(request, 'Invalid class selected.')
            return redirect('assignment')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        deadline_str = request.POST.get('deadline')
        classroom_id = request.POST.get('classroom')
        file = request.FILES.get('file')
        
        try:
            classroom = ClassRoom.objects.get(id=classroom_id, owner=request.user)
            
            # Parse the deadline string to a datetime object
            try:
                # datetime-local format is "YYYY-MM-DDTHH:MM"
                deadline_naive = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
                # Make sure it's timezone aware using the current timezone
                deadline = timezone.make_aware(deadline_naive, timezone.get_current_timezone())
            except (ValueError, TypeError) as e:
                messages.error(request, 'Invalid deadline format. Please use a valid date and time.')
                return render(request, 'assignments/create_assignment.html', {
                    'owned_classes': ClassRoom.objects.filter(owner=request.user),
                    'selected_classroom': selected_classroom,
                })
            
            assignment = Assignment.objects.create(
                classroom=classroom,
                title=title,
                description=description,
                deadline=deadline,
                created_by=request.user,
                file=file
            )
            
            # Send notifications to all class members
            notification_title = f"New Assignment: {title}"
            notification_message = f"A new assignment '{title}' has been posted in {classroom.name}. Due: {assignment.deadline.strftime('%B %d, %Y at %H:%M')}"
            
            notifications_sent = Notification.create_notifications_for_class(
                classroom=classroom,
                sender=request.user,
                notification_type='assignment',
                title=notification_title,
                message=notification_message,
                content_object=assignment
            )
            
            messages.success(request, f'Assignment "{title}" created successfully! {notifications_sent} students notified.')
            
            # Redirect back to class assignments if created from class page
            if class_id:
                return redirect('class_assignments', class_id=class_id)
            else:
                return redirect('assignment')
                
        except ClassRoom.DoesNotExist:
            messages.error(request, 'You can only create assignments for your own classes.')
        except Exception as e:
            messages.error(request, f'Error creating assignment: {str(e)}')
            import traceback
            print(f"Assignment creation error: {traceback.format_exc()}")  # For debugging
    
    # Get user's owned classes for the form
    owned_classes = ClassRoom.objects.filter(owner=request.user)
    return render(request, 'assignments/create_assignment.html', {
        'owned_classes': owned_classes,
        'selected_classroom': selected_classroom,
    })

@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check if user has access to this assignment
    owned_classes = ClassRoom.objects.filter(owner=request.user)
    joined_memberships = ClassMembership.objects.filter(user=request.user)
    joined_classes = ClassRoom.objects.filter(id__in=joined_memberships.values_list('classroom_id', flat=True))
    all_user_classes = (owned_classes | joined_classes).distinct()
    
    if assignment.classroom not in all_user_classes:
        messages.error(request, 'You do not have access to this assignment.')
        return redirect('assignment')
    
    is_owner = assignment.classroom.owner == request.user
    user_submission = None
    is_overdue = timezone.now() > assignment.deadline
    
    # Get user's submission if they are not the owner
    if not is_owner:
        try:
            user_submission = Submission.objects.get(
                assignment=assignment, 
                student=request.user
            )
        except Submission.DoesNotExist:
            pass
    
    # Handle submission
    if request.method == 'POST' and 'submit_assignment' in request.POST:
        if is_owner:
            messages.error(request, 'Class owners cannot submit assignments.')
            return redirect('assignment_detail', assignment_id=assignment_id)
        
        if user_submission:
            messages.error(request, 'You have already submitted this assignment.')
            return redirect('assignment_detail', assignment_id=assignment_id)
        
        if is_overdue:
            messages.error(request, 'Assignment deadline has passed.')
            return redirect('assignment_detail', assignment_id=assignment_id)
        
        if 'submission_file' in request.FILES:
            Submission.objects.create(
                assignment=assignment,
                student=request.user,
                file=request.FILES['submission_file'],
                remarks=request.POST.get('remarks', '')
            )
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('assignment_detail', assignment_id=assignment_id)
        else:
            messages.error(request, 'Please select a file to submit.')
    
    # Get all submissions if user is the owner
    submissions = None
    if is_owner:
        submissions = Submission.objects.filter(assignment=assignment).order_by('-submitted_at')
    
    context = {
        'assignment': assignment,
        'user_submission': user_submission,
        'submissions': submissions,
        'is_overdue': is_overdue,
        'is_owner': is_owner,
    }
    
    return render(request, 'assignments/assignment_detail.html', context)

@login_required
def assignment_calendar(request):
    """Calendar view showing assignment deadlines and submission dates"""
    # Get user's classes
    owned_classes = ClassRoom.objects.filter(owner=request.user)
    joined_memberships = ClassMembership.objects.filter(user=request.user)
    joined_classes = ClassRoom.objects.filter(id__in=joined_memberships.values_list('classroom_id', flat=True))
    all_user_classes = (owned_classes | joined_classes).distinct()
    
    # Get current month and year from request, default to current date
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Get assignments for the specified month
    assignments = Assignment.objects.filter(
        classroom__in=all_user_classes,
        deadline__year=year,
        deadline__month=month
    ).order_by('deadline')
    
    # Get submissions for the user in the specified month
    submissions = Submission.objects.filter(
        student=request.user,
        assignment__classroom__in=all_user_classes,
        submitted_at__year=year,
        submitted_at__month=month
    ).order_by('submitted_at')
    
    # Create calendar events
    events = []
    
    # Add assignment deadlines
    for assignment in assignments:
        events.append({
            'title': f'{assignment.title}',
            'date': assignment.deadline.strftime('%Y-%m-%d'),
            'type': 'deadline',
            'class': assignment.classroom.name,
            'description': f'Assignment deadline for {assignment.classroom.name}',
            'url': f'/assignment/{assignment.id}/'
        })
    
    # Add submission dates
    for submission in submissions:
        events.append({
            'title': f'{submission.assignment.title}',
            'date': submission.submitted_at.strftime('%Y-%m-%d'),
            'type': 'submission',
            'class': submission.assignment.classroom.name,
            'description': f'Submitted assignment for {submission.assignment.classroom.name}',
            'url': f'/assignment/{submission.assignment.id}/'
        })
    
    # Create calendar data
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Navigation dates
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    context = {
        'calendar': cal,
        'events': json.dumps(events),  # For JavaScript
        'events_list': events,  # For template iteration
        'year': year,
        'month': month,
        'month_name': month_name,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'today': today,
    }
    
    return render(request, 'assignments/calendar.html', context)