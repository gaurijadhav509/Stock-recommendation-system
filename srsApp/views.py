# srsApp/views.py
from django.shortcuts import render
from .models import *
from django.contrib import messages

def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == "POST":
        email_v = request.POST['u_email']
        password_v = request.POST['u_password']

        if Users.objects.filter(email=email_v).exists():
            user = Users.objects.get(email=email_v)
            
            if user.password == password_v:
                messages.success(request, 'Login Successful!')
                return redirect('/srsApp/login_success')
            else:
                messages.warning(request, 'Invalid username or password!')
                return redirect('/srsApp/login')
        else:
            messages.warning(request, 'Invalid username or password!')
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

        if Users.objects.filter(email=email_v).exists():
            messages.warning(request, 'User already exists.')
            return render(request, 'signup.html')
        elif password_v != conf_pass_v:
            messages.warning(request, 'Passwords do not match.')
            return render(request, 'signup.html')
        else:
            us = Users(name=name_v, email=email_v, password=password_v)
            us.save()
            messages.success(request, 'User Registered successfully!')
            return redirect('/srsApp/login_success')

    return render(request, 'signup.html')

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
