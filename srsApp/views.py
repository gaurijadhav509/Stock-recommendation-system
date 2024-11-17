from django.shortcuts import render, redirect
from .models import *
from .services import *
from .sql_queries import *
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
from django.utils import timezone


# from dotenv import load_dotenv

os.environ["API_KEY"] = 'AIzaSyDBcF3Q3fYpZ1VYVBKZ18op2rouCm1cC5k'
genai.configure(api_key=os.environ["API_KEY"])

# # Load environment variables from the .env file
# load_dotenv()

# # Fetch the API key from the environment variable
# api_key = os.getenv('API_KEY')


def home_view(request):
    return render(request, 'home.html')


def login_view(request):
    if request.method == "POST":
        email_v = request.POST['u_email']
        password_v = request.POST['u_password']

        if check_user_exists(email_v):
            user = get_one_user(email_v)
            if user["password"] == password_v:
                messages.success(request, 'Login Successful!')
                return redirect('investment_preferences_view')  # Redirect to investment preferences
            else:
                messages.warning(request, 'Invalid username or password!')
                return redirect('login')
        else:
            messages.warning(request, 'Invalid username or password!')
            return redirect('login')
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

            if check_user_exists(email_v):
                messages.warning(request, 'User already exists.')
                return render(request, 'signup.html')
            elif password_v != conf_pass_v:
                messages.warning(request, 'Passwords do not match.')
                return render(request, 'signup.html')
            else:
                try:
                    insert_user(name=name_v, email=email_v, password=password_v)
                except:
                    messages.warning(request, 'Something went wrong.')
                    return render(request, 'signup.html')

                messages.success(request, 'User registered successfully!')
                return redirect('login')  # Redirect to login page

        except ValidationError:
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

        # Step 2: Save investment preference using raw SQL
        try:
            preference_id = upsert_investment_preferences(user_instance.user_id, risk_tolerance, asset_type, preferred_region, preferred_exchange)
        except Exception as e:
            return render(request, 'investment_preferences.html', {'error': f"An unexpected error occurred: {str(e)}"})

        investment_preference = Investment_Preferences(
            risk_tolerance=risk_tolerance,
            asset_type=asset_type,
            preferred_region=preferred_region,
            preferred_exchange=preferred_exchange
        )


        # Step 3: Fetch recommendations from Gemini
        try:
            recommendations = get_recommendations_from_gemini(investment_preference)
        except Exception as e:
            return render(request, 'investment_preferences.html', {'error': f"An error occurred while fetching recommendations: {str(e)}"})

        # Step 4: Save the recommended stocks
        for stock in recommendations:
            stock_id = insert_stock_and_map_to_investment_preference(
            stock['symbol'], 
            stock['company'], 
            stock.get('sector', ''), 
            stock.get('market_cap', 0), 
            preference_id
    )

        return render(request, 'investment_preferences.html', {'stocks': recommendations, 'error': None})

    return render(request, 'investment_preferences.html')


def view_bookmarked_stocks(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Fetch all stocks (you can filter if needed, for example by sector or market_cap)
        stocks = Stocks.objects.all()  # Fetch all stocks in the database
    else:
        # If the user is not logged in, show a default set of stocks (e.g., the first 5)
        stocks = Stocks.objects.all()[:5]  # Show first 5 stocks for non-logged-in users

    # Prepare the data to pass to the template
    stocks_data = [
        {
            "symbol": stock.stock_symbol,
            "name": stock.company_name,
            "sector": stock.sector,
            "market_cap": stock.market_cap,
            "created_at": stock.created_at,
        }
        for stock in stocks
    ]

    # Render the template with the stocks data
    return render(request, 'view_bookmarked_stocks.html', {'bookmarked_stocks': stocks_data})
    
@csrf_exempt
def save_bookmarks(request):
    if request.method == "POST":
        # Retrieve the user instance
        user_instance = Users.objects.get(user_id=1)

        # Print the raw request body
        print("Raw request body:", request.body)

        # Parse the JSON payload
        try:
            data = json.loads(request.body)
            print("Parsed data:", data)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        
        bookmarked_stocks = data.get("bookmarkedStocks", [])
        #user_id = request.user.id  # or retrieve user ID if user is logged in

        # Validate data
        if not bookmarked_stocks or any(stock_id is None for stock_id in bookmarked_stocks):
            return JsonResponse({"error": "Invalid bookmarkedStocks data"}, status=400)

        for stock_id in bookmarked_stocks:
            Bookmarked_Stock.objects.create(user_id=user_instance.user_id, stock_id=stock_id)
        
        print("bookmarked successssssssss")
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


#def view_bookmarks(request):
    user_id = request.user.id
    bookmarks = Bookmarked_Stock.objects.filter(user_id=user_id)
    return render(request, "bookmarks.html", {"bookmarks": bookmarks})
