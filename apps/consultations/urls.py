
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CreateConsultationView,PatientConsultationListView, home_page

urlpatterns = [

    path('',home_page.as_view(),name='home'),
    path('consultations/',CreateConsultationView.as_view(),name='consultations'),
    path('consultations/admin',PatientConsultationListView.as_view(),name='consultations_admin'),
]
