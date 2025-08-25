from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, EmailMessage
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from classes.models import ClassRoom, ClassMembership

# handles user login part 

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')  
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html')
# create or join the class after logging in to the system
@login_required
def dashboard(request):
    if request.method == 'POST' and 'join_class' in request.POST:
        invite_code = request.POST.get('invite_code')
        try:
            classroom = ClassRoom.objects.get(invite_code=invite_code)
            if classroom.owner == request.user or ClassMembership.objects.filter(user=request.user, classroom=classroom).exists():
                messages.info(request, "You are already a member of this class.")
            else:
                ClassMembership.objects.create(user=request.user, classroom=classroom)
                messages.success(request, f"You have joined {classroom.name}!")
        except ClassRoom.DoesNotExist:
            messages.error(request, "Invalid class code.")
        return redirect('dashboard')
    owned_classes = ClassRoom.objects.filter(owner=request.user)
    memberships = ClassMembership.objects.filter(user=request.user)
    joined_classes = ClassRoom.objects.filter(id__in=memberships.values_list('classroom_id', flat=True))
    all_classes = (owned_classes | joined_classes).distinct()
    return render(request, 'base/dashboard.html', {'all_classes': all_classes})

#handles the registration.
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=False  # User is inactive until email is verified
            )
            token = default_token_generator.make_token(user)
            verify_url = request.build_absolute_uri(
                reverse('verify_email', args=[user.pk, token])
            )
            email_message = EmailMessage(
                subject='Verify your email',
                body=f'Click the link to verify your email: {verify_url}',
                from_email='registertolms@gmail.com',
                to=[user.email]
            )
            email_message.send()
            messages.success(request, 'Check your email to verify your account.')
            return redirect('login')
    return render(request, 'users/register.html')

def verify_email(request, uid, token):
    user = get_object_or_404(CustomUser, pk=uid)
    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Email verified! You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid or expired verification link.')
        return redirect('register')

@login_required(login_url='login')
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


