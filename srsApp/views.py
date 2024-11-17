from django.shortcuts import render, redirect
from .models import *
from .services import *
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
import os
from django.conf import settings
import json
import openai
from decimal import Decimal
import google.generativeai as genai

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Bookmarked_Stock, Stocks, Users


from django.contrib.auth.models import User

os.environ["API_KEY"] = 'AIzaSyDBcF3Q3fYpZ1VYVBKZ18op2rouCm1cC5k'
genai.configure(api_key=os.environ["API_KEY"])


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

            if (Users.objects.filter(email=email_v).exists()):
                messages.warning(request, 'User already exists.')
                return render(request, 'signup.html')
            elif(password_v != conf_pass_v):
                messages.warning(request, 'Password doesn\'t match.')
                return render(request, 'signup.html')
            else:
                us = Users(name=name_v, email = email_v, password = password_v)
                us.save()
                messages.success(request, 'User Registerd successfully!')
                return redirect('/srsApp/login_success')

        except ValidationError as e:
            messages.warning(request, 'Email is invalid')
            return render(request, 'signup.html')

    return render(request, 'signup.html')


def investment_preferences_view(request):
    return render(request, 'investment_preferences.html')

def submit_investment_preferences(request):
    if request.method == 'POST':
        # Retrieve the user instance
        user_instance = Users.objects.get(user_id=1)
        
        # Retrieve form data
        risk_tolerance = int(request.POST.get('risk_tolerance'))
        asset_type = int(request.POST.get('asset_type'))
        preferred_region = request.POST.get('preferred_region', '').strip()
        preferred_exchange = request.POST.get('preferred_exchange', '').strip().upper()

        # Step 1: Validate the preferred_exchange against the preferred_region
        validation_error = validate_exchange_region(preferred_exchange, preferred_region)
        if validation_error:
            return render(request, 'investment_preferences.html', {'error': validation_error})

        # Step 2: Save investment preference if valid
        investment_preference = Investment_Preferences.objects.create(
            user_id=user_instance.user_id,
            risk_tolerance=risk_tolerance,
            asset_type=asset_type,
            preferred_region=preferred_region,
            preferred_exchange=preferred_exchange
        )

        # Step 3: Fetch recommendations from Gemini
        try:
            recommendations = get_recommendations_from_gemini(investment_preference)
        except Exception as e:
            return render(request, 'investment_preferences.html', {'error': f"An unexpected error occurred: {str(e)}"})

        # Step 4: Save the recommended stocks
        for stock in recommendations:
            Stocks.objects.create(
                stock_symbol=stock['symbol'],
                company_name=stock['company'],
                sector=stock.get('sector', ''),
                market_cap=stock.get('market_cap')
            )

        return render(request, 'investment_preferences.html', {'stocks': recommendations, 'error': None})

    return render(request, 'investment_preferences.html')

@csrf_exempt
def save_bookmarks(request):
    if request.method == "POST":
        data = json.loads(request.body)
        bookmarked_stocks = data.get("bookmarkedStocks", [])
        user_id = request.user.id  # or retrieve user ID if user is logged in

        for stock_id in bookmarked_stocks:
            Bookmarked_Stock.objects.create(user_id=user_id, stock_id=stock_id)
        
        print("bookmarked successssssssss")
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


#def view_bookmarks(request):
    user_id = request.user.id
    bookmarks = Bookmarked_Stock.objects.filter(user_id=user_id)
    return render(request, "bookmarks.html", {"bookmarks": bookmarks})
