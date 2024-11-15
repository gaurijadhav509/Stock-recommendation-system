from django.shortcuts import render, redirect
from .models import *
from .sql_queries import *
from .services import *
from django.contrib import messages
import os
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

os.environ["API_KEY"] = 'AIzaSyDBcF3Q3fYpZ1VYVBKZ18op2rouCm1cC5k'
genai.configure(api_key=os.environ["API_KEY"])

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
                return redirect('/srsApp/investment_preferences', {})
            else:
                messages.warning(request, 'invalid username or password!')
                return redirect('/srsApp/login')
                
        else:
            messages.warning(request, 'invalid username or password!')
            print("hereee1")
            return redirect('/srsApp/login')
    else:
        return render(request, "login.html")


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
                    messages.success(request, 'User Registerd successfully!')
                    return redirect('/srsApp/investment_preferences')
                except:
                    messages.warning(request, 'Something went wrong.')
                    return render(request, 'signup.html')    

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
            # preferred_exchange=preferred_exchange
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