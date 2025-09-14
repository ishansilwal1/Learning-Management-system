from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Assignment, Submission
from classes.models import ClassRoom, ClassMembership
from notification.models import Notification

@login_required
def assignment(request):
    # Get user's owned classes
    owned_classes = ClassRoom.objects.filter(owner=request.user)
    
    # Get user's joined classes
    joined_memberships = ClassMembership.objects.filter(user=request.user)
    joined_classes = ClassRoom.objects.filter(id__in=joined_memberships.values_list('classroom_id', flat=True))
    
    # Get all assignments from user's classes
    all_user_classes = (owned_classes | joined_classes).distinct()
    assignments = Assignment.objects.filter(classroom__in=all_user_classes).order_by('-created_at')
    
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
        'owned_classes': owned_classes,
    }
    return render(request, 'assignments/assignment.html', context)

@login_required
def create_assignment(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        deadline = request.POST.get('deadline')
        classroom_id = request.POST.get('classroom')
        file = request.FILES.get('file')
        
        try:
            classroom = ClassRoom.objects.get(id=classroom_id, owner=request.user)
            
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
            return redirect('assignment')
        except ClassRoom.DoesNotExist:
            messages.error(request, 'You can only create assignments for your own classes.')
        except Exception as e:
            messages.error(request, f'Error creating assignment: {str(e)}')
    
    # Get user's owned classes for the form
    owned_classes = ClassRoom.objects.filter(owner=request.user)
    return render(request, 'assignments/create_assignment.html', {
        'owned_classes': owned_classes
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