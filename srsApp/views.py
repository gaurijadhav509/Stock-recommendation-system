from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.contrib.auth.models import User

def home_view(request):
    return render(request, 'home.html') 

def login_view(request):
    if request.method == "POST":
        email_v = request.POST['u_email']
        password_v = request.POST['u_password']

        # user1 = User.objects.raw('SELECT * FROM users').columns
        # user = Users.objects.raw('SELECT * FROM stock_recommendation_system_db.users')[0]
        # user2 = Users.objects.all()
        # user3 = Users.objects.filter(email=email_v).exists()
        # print(user)
        # print(user2[0].email)
        # print(user3)
        # print(user1)
        # print(User.objects.all())

        # print(request)
        # print(authenticate(request, username=email_v, password=password_v))
        # print(authenticate(request, email=email_v, password=password_v))

        # user = authenticate(request, username=email_v, password=password_v)
        if (Users.objects.filter(email=email_v).exists()):
            print("hereee")
            user = Users.objects.get(email=email_v)
            
            if(user.password == password_v):
                return redirect('/srsApp/login_success')
            else:
                return redirect('/srsApp/login')
                
        else:
            print("hereee1")
            return redirect('/srsApp/login')
    else:
        return render(request, "login.html")


def login_user(request):
    email_v = request.POST['u_email']
    password_v = request.POST['u_password']

    user = authenticate(request, username=email_v, password=password_v)
    print(user)
        
    if user is not None:
        login(request, user)
        return redirect('login_success')  # Redirect to a success page
    else:
        messages.error(request, 'Invalid username or password')
        return redirect('/login')
    

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