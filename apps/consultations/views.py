import datetime
from django.shortcuts import  redirect
from django.contrib import messages
from django.urls import reverse
from django.views.generic import TemplateView
from apps.consultations.models import Consultation
from apps.users.models import CustomUser, Doctor, Patient
from .forms import ConsultationForm
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView,ListView

# Consultations views.
class home_page(TemplateView):
    template_name = 'homepage/home.html'


class CreateConsultationView(LoginRequiredMixin,TemplateView):
    template_name = 'homepage/consultations.html'  # Consultations current template

    """_Some validations applied over the form_
    """
    def form_valid(self, form):
        # Check if the patient has been consulted within the last 30 minutes
        patient = form.cleaned_data['patient']
        recent_consultation = Consultation.objects.filter(
            patient=patient,
            consultation_date__gte=Consultation.consultation_date - timedelta(minutes=30)
        ).exists()

        if recent_consultation:
            messages.warning('patient', 'Patient has been consulted within the last 30 minutes.')
            return self.form_invalid(form)

        return super().form_valid(form)
    
    """_Context data needed when loading the form (GET) Method_
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.user_type == 'doctor':
            try:
                # Get the current doctor from the request (assuming you have access to it)
                doctor = Doctor.objects.get(user=self.request.user) # This assumes the doctor is the logged-in user
                # Providing the list of consultations as 'object_list'
                context['object_list'] = Consultation.objects.filter(doctor=doctor)
            except Doctor.DoesNotExist:
                 doctor = None
                 
        elif user.user_type == 'patient':
            try:
                # Get the current doctor from the request (assuming you have access to it)
                patient = Patient.objects.get(user=user)
                 # Providing the list of consultations as 'object_list'
                context['object_list'] = Consultation.objects.filter(patient=patient)
            except Patient.DoesNotExist:
                patient = None
          
        # Initialize the form with the current doctor
        form = ConsultationForm()
        # Providing the form
        context['form'] = form
        return context

    """_Saving consultation with custom logic (POST) Method_
    """
    def post(self, request, *args, **kwargs):
        
        #doctor = Doctor.objects.get(user=request.user) #Getting the current doctor in session
        
        # Check if the user has a Doctor profile (PLAN A)
        try:
           doctor = Doctor.objects.get(user=request.user) #Getting the current doctor in session
        except Doctor.DoesNotExist:
            messages.warning(request, "You must complete your profile before creating a consultation.")
            return redirect('profile')  # Redirect to the profile completion page
            
        # Optionally, check if the profile is fully completed (PLAN B)
        if not doctor.is_profile_complete():
            messages.warning(request, "You must complete your profile before creating a consultation.")
            return redirect('profile_completion_page')  # Redirect to the profile completion page
        
        # Handling form submission
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            patient = form.cleaned_data['patient'] # Getting the current patient selected for consultation
            
            # Check for existing consultation
            existing_consultation = Consultation.objects.filter(
                doctor=doctor,
                patient=patient,
                consultation_date__gte=consultation.consultation_date - timedelta(minutes=5)
            ).first() # Returns the first matching consultation (if any)
            
            # If existing_consultation is not None (meaning a duplicate exists), we display an error message and re-render the form with the errors.
            if existing_consultation:
                messages.warning(request, f"A consultation with {patient} on {consultation.consultation_date.strftime('%Y-%m-%d')} already exists in this moment. Wait 5 mins")
                context = self.get_context_data()
                context['form'] = form
                return self.render_to_response(context)
            
            # If no duplicate is found, the code proceeds to save the consultation as before
            consultation.doctor = doctor
            consultation.save()
            messages.success(request,f'Dr: {consultation.doctor.user.get_full_name()} consultation with {patient} successfully achieved at {consultation.consultation_date.strftime('%Y-%m-%d')}')
            return redirect(reverse('consultations'))  # Consultations URL name
        # If the form is not valid, return the same context with the form errors
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)