from django.shortcuts import render, redirect
from .models import *
from .sql_queries import *
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User

def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == "POST":
        email_v = request.POST['u_email']
        password_v = request.POST['u_password']

        if (check_user_exists(email_v)):
            print("hereee")
            user = get_one_user(email_v)
            
            if(user["password"] == password_v):
                messages.success(request, 'Login Successful!')
                return redirect('/srsApp/login_success', {})
            else:
                messages.warning(request, 'invalid username or password!')
                return redirect('/srsApp/login')
                
        else:
            messages.warning(request, 'invalid username or password!')
            print("hereee1")
            return redirect('/srsApp/login')
    else:
        return render(request, "login.html")

def login_success(request):
    return render(request, 'login_success.html')


def user_signup_view(request):
    if request.method == "POST":
        name_v = request.POST['u_name']
        email_v = request.POST['u_email']
        password_v = request.POST['u_password']
        conf_pass_v = request.POST['conf_password']

        validator = EmailValidator(message='Enter a valid email address.')

        try:
            validator(email_v)

            if (check_user_exists(email_v)):
                messages.warning(request, 'User already exists.')
                return render(request, 'signup.html')
            elif(password_v != conf_pass_v):
                messages.warning(request, 'Password doesn\'t match.')
                return render(request, 'signup.html')
            else:
                try:
                    insert_user(name=name_v, email=email_v, password=password_v)
                except:
                    messages.warning(request, 'Something went wrong.')
                    return render(request, 'signup.html')
                    
                messages.success(request, 'User Registerd successfully!')
                return redirect('/srsApp/login_success')

        except ValidationError as e:
            messages.warning(request, 'Email is invalid')
            return render(request, 'signup.html')

    return render(request, 'signup.html')