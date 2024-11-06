from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login
from django.contrib import messages

def home_view(request):
    return render(request, 'home.html') 

def login_view(request):
    # add login logic
    return render(request, 'login.html')

def login_user(request):
    email_v = request.POST['u_email']
    password_v = request.POST['u_password']

    user = authenticate(request, username=email_v, password=password_v)
        
    if user is not None:
        login(request, user)
        return redirect('home')  # Redirect to a success page
    else:
        messages.error(request, 'Invalid username or password')
    
    return render(request, 'login_success.html', {})

def login_success(request):
    return render(request, 'login_success.html')


def user_signup_view(request):
    return render(request, 'signup.html')

def insert_user(request):
    name_v = request.POST['u_name']
    email_v = request.POST['u_email']
    password_v = request.POST['u_password']

    us = Users(name=name_v, email = email_v, password = password_v)
    us.save()
    return render(request, 'home.html', {})