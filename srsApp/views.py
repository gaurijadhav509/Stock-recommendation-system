from django.shortcuts import render

def home_view(request):
    return render(request, 'srsApp/home.html') 

def login_view(request):
    # add login logic
    return render(request, 'srsApp/login.html') 
