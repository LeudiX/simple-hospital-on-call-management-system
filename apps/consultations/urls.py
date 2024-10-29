
from django.urls import path
from . import views
from .views import CreateConsultationView,PatientConsultationListView, home_page

urlpatterns = [

    path('',home_page.as_view(),name='home'),
    path('consultations/',CreateConsultationView.as_view(),name='consultations'),
    path('consultations/admin/',PatientConsultationListView.as_view(),name='consultations_admin'),
    path('consultations/admin/<int:id>/details/', views.details_ptconsultation, name='consultation_details'), # URL for load consultation details
    path('consultations/admin/<int:id>/delete/', views.delete_ptconsultation, name='delete_consultation'), # URL for delete a consultation
    path('consultations/admin/delete-consultations/confirm', views.delete_ptconsultations, name='delete_consultations'), # URL for handle multiple consultations removal
]
