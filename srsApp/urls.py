from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),       
    path('login/', views.login_view, name='login'),
    path('login_success/', views.login_success, name="login_success"), 
    path('login_user/', views.login_user, name="login_user"), 
    path('signup/', views.user_signup_view, name="user_signup_view"), 
    path("insert_user/", views.insert_user, name= "insert_user"),
]
