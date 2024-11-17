# srsApp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'), 
    path('signup/', views.user_signup_view, name="user_signup_view"),
    path('investment_preferences/', views.investment_preferences_view, name='investment_preferences_view'),
    path('submit_investment_preferences/', views.submit_investment_preferences, name='submit_investment_preferences'),
    path('bookmarked_stocks/', views.view_bookmarked_stocks, name='view_bookmarked_stocks'),
]
