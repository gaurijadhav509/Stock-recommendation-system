from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),       
    path('login/', views.login_view, name='login'),
    path('signup/', views.user_signup_view, name='user_signup_view'),
    path('investment_preferences/', views.investment_preferences_view, name='investment_preferences_view'),
    path('submit_investment_preferences/<int:user_id>', views.submit_investment_preferences, name='submit_investment_preferences'),

    path('user_profile/<str:email_v>/', views.user_profile, name='user_profile'),
]
