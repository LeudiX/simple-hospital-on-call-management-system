
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('register/',views.register, name='register'), # URL for users registration
    path('users/',views.list_users, name='users'), # URL  for existing users list view
    path('users/<int:id>/edit/',views.edit_user, name='edit_user'), # URL for updating a user
    path('users/<int:id>/delete/', views.delete_user, name='delete_user'),  # URL for deleting a user
    path('users/delete-users/confirm', views.delete_users, name='delete_users'), # URL for handle multiple user removal
    path('profile/',views.profile_view, name='profile'), # Showing the current user's profile
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'),name='login'), # URL for users Login view
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'),name='logout'), # URL for users Logout view
]
