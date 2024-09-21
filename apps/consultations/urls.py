
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from .views import home_page

urlpatterns = [

    path('',home_page.as_view(),name='home'),
   
]
