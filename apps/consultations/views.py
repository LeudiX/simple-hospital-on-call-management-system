import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic import TemplateView
from apps.consultations.models import Consultation
from apps.users.models import CustomUser, Doctor, Patient
from .forms import ConsultationForm
from django.contrib.auth import get_user_model

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView,ListView

# Consultations views.
class home_page(TemplateView):
    template_name = 'homepage/home.html'


class CreateConsultationView(LoginRequiredMixin,TemplateView):
    template_name = 'homepage/consultations.html'  # Consultations current template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Providing the list of consultations as 'object_list'
        context['object_list'] = Consultation.objects.filter(
            doctor=Doctor.objects.get(user=self.request.user)
        )
        # Providing the form
        context['form'] = ConsultationForm()
        # Get all patients
        context['patients'] = Patient.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        # Handling form submission
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.doctor = Doctor.objects.get(user=request.user) #Getting the current doctor in session
            consultation.save()
            messages.success(request,f'Dr: {consultation.doctor.user.get_full_name()} consultation successfully achieved at {consultation.consultation_date.strftime('%Y-%m-%d')}')
            return redirect(reverse('consultations'))  # Consultations URL name
        # If the form is not valid, return the same context with the form errors
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)