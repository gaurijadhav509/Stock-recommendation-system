# srsApp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('login_success/', views.login_success, name="login_success"),
    path('signup/', views.user_signup_view, name="signup"),
    path('bookmarked_stocks/', views.view_bookmarked_stocks, name='view_bookmarked_stocks'),
]
