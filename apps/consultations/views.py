import datetime
from django.shortcuts import  redirect, render
from django.contrib import messages
from django.urls import reverse
from django.views.generic import TemplateView
from apps.consultations.models import Consultation
from apps.users.models import CustomUser, Doctor, Patient
from apps.consultations.models import PatientConsultation
from .forms import CommonConsultationForm, ConsultationForm, PatientConsultationForm, UrgencyConsultationForm, VitalSignsForm
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin


# Consultations views.
class home_page(TemplateView):
    template_name = 'homepage/home.html'


class CreateConsultationView(LoginRequiredMixin,TemplateView):
    template_name = 'homepage/consultations.html'  # Consultations current template
    """
    def get(self, request, *args, **kwargs):
        # Initialize forms
        consultation_form = ConsultationForm()
        patient_consultation_form = PatientConsultationForm()
        urgency_consultation_form = UrgencyConsultationForm()
        common_consultation_form = CommonConsultationForm()
        vital_signs_form = VitalSignsForm()
        
        context = {
            'form': consultation_form,
            'patient_consultation_form': patient_consultation_form,
            'urgency_consultation_form': urgency_consultation_form,
            'common_consultation_form': common_consultation_form,
            'vital_signs_form': vital_signs_form,
        }
        return self.render_to_response(context)
    """
    
    """_Context data needed when loading the form (GET) Method_"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.user_type == 'doctor':
            try:
                # Get the current doctor from the request (assuming you have access to it)
                doctor = Doctor.objects.get(user=user) # This assumes the doctor is the logged-in user
        
                # Providing the list of doctor's consultations as 'consultations' with patient information
                doctor_consultations = Consultation.objects.filter(doctor=doctor).select_related()
                context['consultations'] = doctor_consultations
                      
                # Optionally, get the most recent consultation (or a specific consultation) for the current doctor
                # You can customize this logic based on your needs
                most_recent_consultation = Consultation.objects.filter(doctor=doctor).order_by('-consultation_date').first()
                
                if most_recent_consultation:
                    # Get the corresponding PatientConsultation for the Doctor most recent consultation
                    patient_consultation = PatientConsultation.objects.filter(consultation = most_recent_consultation).last()
                    
                    if patient_consultation: 
                        print(f'{patient_consultation}')                 
                        context['patient'] = patient_consultation.patient
                    else:
                        context['patient'] = None
                else:
                    context['patient'] = None
            
            except Doctor.DoesNotExist:
                    doctor = None
                    context['consultations'] = []
                    context['patient'] = None
                    
        elif user.user_type == 'patient':
            try:
                # Get the current patient from the request (assuming you have access to it)
                patient = Patient.objects.get(user=user)
                
                # Query all consultations for the patient
                all_consultations = PatientConsultation.objects.filter(patient=patient)
                
                # Providing the list of consultations as 'patient_consultation' to the context
                context['patient_consultations'] = all_consultations
                
                # Get the Patient's most recent consultation
                most_recent_consultation = all_consultations.last()
            
                if most_recent_consultation:
                    #print(f'{most_recent_consultation.consultation}') #[Debugging purposes only]
                    context['most_recent_consultation']= most_recent_consultation.consultation
                else:
                    context['most_recent_consultation']= None
            except Patient.DoesNotExist:
                patient = None
                context['patient_consultations'] = []
                context['most_recent_consultation'] = None
          
        # Initialize the form with the current doctor
        context['form'] = ConsultationForm()
        context['patient_consultation_form'] = PatientConsultationForm()
        context['urgency_consultation_form'] = UrgencyConsultationForm()
        context['common_consultation_form'] = CommonConsultationForm()
        context['vital_signs_form'] = VitalSignsForm()
        return context

    """_Saving consultation with custom logic (POST) Method_"""
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
        
        # Handling forms submission
        consultation_form = ConsultationForm(request.POST)
        patient_consultation_form = PatientConsultationForm(request.POST)
        
        if consultation_form.is_valid() and patient_consultation_form.is_valid():
            consultation = consultation_form.save(commit=False)
            patient = patient_consultation_form.cleaned_data['patient']  # Getting the current patient selected for consultation
            
            # Check for existing consultation
            existing_consultation = Consultation.objects.filter(
                doctor=doctor,
                patientconsultation__patient=patient, # Use the related field patient in PatientConsultation!
                consultation_date__gte=consultation.consultation_date - timedelta(minutes=5)
            ).first() # Returns the first matching consultation (if any)
            
            # If existing_consultation is not None (meaning a duplicate exists), we display an error message and re-render the form with the errors.
            if existing_consultation:
                messages.warning(request, f"A consultation with {patient} on {consultation.consultation_date.strftime('%Y-%m-%d')} already exists in this moment. Wait 5 mins")
                context = self.get_context_data()
                context['patient_consultation_form'] = patient_consultation_form
                return self.render_to_response(context)
                    
            # If no duplicate is found, the code proceeds to save the consultation with the doctor as before
            consultation.doctor = doctor
            consultation.status = 'in-progress'
            consultation.save()
            
            # Save the patient consultation
            patient_consultation = patient_consultation_form.save(commit=False)
            patient_consultation.consultation = consultation
            patient_consultation.save()
            
             # Handle different consultation types
            if patient_consultation.consultation_type == 'urgency':
                urgency_consultation_form = UrgencyConsultationForm(request.POST)
                if urgency_consultation_form.is_valid():
                    urgency_consultation = urgency_consultation_form.save(commit=False)
                    urgency_consultation.consultation = consultation
                    urgency_consultation.save()
            elif patient_consultation.consultation_type == 'common':
                common_consultation_form = CommonConsultationForm(request.POST)
                if common_consultation_form.is_valid():
                    common_consultation = common_consultation_form.save(commit=False)
                    common_consultation.consultation = consultation
                    common_consultation.save()
            
            # Save vital signs
            vital_signs_form = VitalSignsForm(request.POST)
            if vital_signs_form.is_valid():
                vital_signs = vital_signs_form.save(commit=False)
                vital_signs.consultation = consultation
                vital_signs.save()
            
            messages.success(request,f'Dr: {consultation.doctor.user.get_full_name()} consultation with {patient} successfully achieved at {consultation.consultation_date.strftime('%Y-%m-%d')}')
            return redirect(reverse('consultations'))  # Consultations URL name
        
        # If the form is not valid, return the same context with the form errors
        context = self.get_context_data()
        context['form'] = consultation_form
        context['patient_consultation_form'] = patient_consultation_form
        
        return self.render_to_response(context)