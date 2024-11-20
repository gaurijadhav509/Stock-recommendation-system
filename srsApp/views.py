from django.shortcuts import render, redirect
from .models import *
from .services import *
from .sql_queries import *
from django.contrib import messages
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import openai
import os
import google.generativeai as genai
from django.contrib.auth.hashers import check_password  # Import for password checking

# Configure GenAI
os.environ["API_KEY"] = 'AIzaSyDBcF3Q3fYpZ1VYVBKZ18op2rouCm1cC5k'
genai.configure(api_key=os.environ["API_KEY"])

# View: Home
def home_view(request):
    return render(request, 'home.html')

# View: Login
def login_view(request):
    if request.method == "POST":
        email_v = request.POST['u_email']
        password_v = request.POST['u_password']
        
        # Authenticate the user using the email and password
        user = authenticate_by_email(request, email_v, password_v)
        
        if user:
            request.session['user_id'] = user.user_id
            messages.success(request, 'Login successful!')
            return redirect('investment_preferences_view')
        else:
            messages.warning(request, 'Invalid username or password!')
            return redirect('login')
    
    return render(request, 'login.html')

def authenticate_by_email(request, email, password):
    try:
        # Find user by email
        user = Users.objects.get(email=email)
    
        if password == user.password:  # Compare the plain text password
            return user
        else:
            return None
    except Users.DoesNotExist:
        return None


# View: User Signup
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
            elif password_v != conf_pass_v:
                messages.warning(request, 'Passwords do not match.')
            else:
                try:
                    insert_user(name=name_v, email=email_v, password=password_v)
                    messages.success(request, 'User registered successfully!')
                    return redirect('login')  # Redirect to login page
                except:
                    messages.warning(request, 'Something went wrong.')
        except ValidationError:
            messages.warning(request, 'Email is invalid')

        return render(request, 'signup.html')

    return render(request, 'signup.html')

# View: Investment Preferences
def investment_preferences_view(request):
    # Check if user is logged in
    user_id = request.session.get('user_id')
    print(user_id)
    if user_id:
        user = Users.objects.get(user_id=user_id)
        return render(request, 'investment_preferences.html', {'user': user})
    else:
        messages.warning(request, 'You must be logged in to access this page.')
        return redirect('login')  # Redirect to login if not logged in


def submit_investment_preferences(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')

        if not user_id:
            messages.warning(request, 'You must be logged in to submit preferences.')
            return redirect('login')

        # Retrieve user instance
        user_instance = Users.objects.get(user_id=user_id)

        risk_tolerance = int(request.POST.get('risk_tolerance'))
        asset_type = int(request.POST.get('asset_type'))
        preferred_region = request.POST.get('preferred_region', '').strip()
        preferred_exchange = request.POST.get('preferred_exchange', '').strip().upper()

        # Step 1: Validate preferred_exchange against preferred_region
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
                preference_id)
            stock['stock_id'] = stock_id

        return render(request, 'investment_preferences.html', {'stocks': recommendations, 'error': None})

    return render(request, 'investment_preferences.html')


# View: View Bookmarked Stocks
def view_bookmarked_stocks(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.warning(request, 'You must be logged in to view bookmarked stocks.')
        return redirect('login')

    # Fetch bookmarked stocks using the utility function
    bookmarked_stocks = get_bookmarked_stocks_for_user(user_id)
    return render(request, 'view_bookmarked_stocks.html', {'bookmarked_stocks': bookmarked_stocks})

# API: Save Bookmarks
@csrf_exempt
def save_bookmarks(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return JsonResponse({"error": "You must be logged in to save bookmarks."}, status=403)

    if request.method == "POST":
        # Parse the JSON payload
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        bookmarked_stocks = data.get("bookmarkedStocks", [])
        result = save_user_bookmarked_stocks(user_id, bookmarked_stocks)

        if result["success"]:
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"error": result.get("error", "Failed to save bookmarks")}, status=500)

    return JsonResponse({"success": False})

    # View: Logout
def logout_view(request):
    # Clear the session to log out the user
    request.session.flush() 
    request.session.flush()
    list(messages.get_messages(request))
    
    # Redirect to the login page
    return redirect('home')
