
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CreateConsultationView, home_page

urlpatterns = [

    path('',home_page.as_view(),name='home'),
    path('consultations/',CreateConsultationView.as_view(),name='consultations'),
]
