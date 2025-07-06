from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from dashboard.models import *

# Registration View
def register_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        if Students.objects.filter(student=email).exists():
            if User.objects.filter(username=email).exists():
                messages.error(request, 'Username already exists.')
                return redirect('accounts:register')

            user = User.objects.create_user(username=email, email=email, password=password)
            user.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'You must be registered to create an account.')
            return redirect('accounts:register')

    return render(request, 'home/index.html')


# Login View
def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if User.objects.filter(first_name='admin').exists() or User.objects.filter(first_name='lecturer').exists():
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('dashboard:menu')  # Redirect to the dashboard menu
            elif Students.objects.filter(student=email).exists():
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('dashboard:menu')  # Redirect to the dashboard menu
            else:
                messages.error(request, 'You must be registered to log in.')
                return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('accounts:login')
        

    return render(request, 'home/index.html')


# Logout View
def logout_user(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('accounts:login')
