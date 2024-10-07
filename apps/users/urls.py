
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('register/',views.register, name='register'),
    path('users/',views.users_list, name='users'),
    path('profile/',views.profile_view, name='profile'), # Showing the current user's profile
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'),name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'),name='logout'),
]
