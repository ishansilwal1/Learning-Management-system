from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import CustomUser

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('check')  # Change 'dashboard' to your dashboard view name
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html')

def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'base/dashboard.html')
    else:
        messages.error(request, 'You need to log in first.')
        return redirect('login')

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
            user = CustomUser(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            user.set_password(password)
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    return render(request, 'users/register.html')
