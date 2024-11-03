from django.shortcuts import render
from .models import *

def home_view(request):
    return render(request, 'home.html') 

def login_view(request):
    # add login logic
    return render(request, 'login.html') 

def user_signup_view(request):
    return render(request, 'signup.html')

def insert_user(request):
    name_v = request.POST['u_name']
    email_v = request.POST['u_email']
    password_v = request.POST['u_password']

    us = Users(name=name_v, email = email_v, password = password_v)
    us.save()
    return render(request, 'home.html', {})