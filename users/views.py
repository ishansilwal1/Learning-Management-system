from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, EmailMessage
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

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

@login_required(login_url='login') 
def dashboard(request):
    return render(request, 'base/dashboard.html')

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
                to=[user.email],
                headers={
                    'X-Priority': '1 (Highest)',
                    'X-MSMail-Priority': 'High',
                    'Importance': 'High'
                }
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

@login_required(login_url='login')
def account_settings(request):
    user = request.user
    if request.method == 'POST':
        # Handle profile image upload
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        # Handle password change
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        if new_password1 and new_password1 == new_password2:
            user.set_password(new_password1)
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, "Password updated successfully.")
        elif new_password1 or new_password2:
            messages.error(request, "Passwords do not match.")
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('dashboard')
    return redirect('dashboard')
