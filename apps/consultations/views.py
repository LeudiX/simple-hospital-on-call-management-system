
from django.shortcuts import  redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView,ListView
from apps.consultations.models import Consultation, PatientConsultation, UrgencyConsultation, CommonConsultation, VitalSigns
from apps.users.models import  Doctor, Patient
from .forms import CommonConsultationForm, ConsultationForm, PatientConsultationForm, UrgencyConsultationForm, VitalSignsForm
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db.models.functions import Concat
from django.db.models import Value

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
        
                # Providing the list of doctor's consultations as 'consultations' with patient information ordered by consultation_date
                doctor_consultations = Consultation.objects.filter(doctor=doctor).select_related().order_by('-consultation_date')
                context['consultations'] = doctor_consultations
                      
                # Optionally, get the most recent consultation (or a specific consultation) for the current doctor
                # You can customize this logic based on your needs
                most_recent_consultation = Consultation.objects.filter(doctor=doctor).order_by('-consultation_date').first()
                
                if most_recent_consultation:
                    # Get the corresponding PatientConsultation for the Doctor most recent consultation
                    patient_consultation = PatientConsultation.objects.filter(consultation = most_recent_consultation).last()
                    
                    if patient_consultation:                
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
            consultation.status = 'completed'
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

class PatientConsultationListView(LoginRequiredMixin,ListView):
    model = PatientConsultation
    
    # The context object name that will be used in the templates to query the consultations on system admin
    context_object_name = 'patient_consultations'
    template_name  = 'homepage/list_patient_consultations.html'
    paginate_by = 4
    
    # Common queries applied over patient_consultations 
    def get_queryset(self):
        
        # Get search query
        search_query = self.request.GET.get('search_query','') # Get value from the name attribute of the input field or None
        
        # Base queryset
        queryset = PatientConsultation.objects.all()
        
        # Filter by patient or doctor name based on search query
        if search_query:
            queryset = queryset.filter(
                Q(patient__user__first_name__icontains=search_query)|
                Q(patient__user__last_name__icontains=search_query)|
                Q(consultation__doctor__user__first_name__icontains=search_query)|       
                Q(consultation__doctor__user__last_name__icontains=search_query)       
            )
            # print(f'{queryset}') # Debugging
            
        # Get filter parameters from the request
        consultation_type = self.request.GET.get('consultation_type','') # Get value from the name attribute of the input field or None
        
        # Filter by consultation_type if specified
        if consultation_type:
           queryset = queryset.filter(consultation_type=consultation_type) # Return only the consultations of the specified type
           print(f'{queryset}')
        
        # Define allowed sort fields
        sort_by = self.request.GET.get('sort', 'consultation_date')  # Default sort field
        order = self.request.GET.get('order', 'asc')  # Default order
        
        # Sorting logic
        if sort_by == 'attended_by':
            # Annotate with full name for sorting
            queryset = queryset.annotate(
                attended_by=Concat(
                    'consultation__doctor__user__first_name', 
                    Value(' '), 
                    'consultation__doctor__user__last_name'
                )
            )
            sort_field = 'attended_by'
        else:
            sort_field = 'consultation__consultation_date'
        
        # Apply ordering
        if order == 'desc':
            sort_field = f'-{sort_field}' # Indicate descending order of sorteable field
    
        return queryset.order_by(sort_field)  # Get all the consultations ordered by sort field
    
    # Get the context data and add the consultation_type and search_query to it
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)     
        context['sort_by'] = self.request.GET.get('sort', 'consultation_date') # Add sort_by to the context
        context['order'] = self.request.GET.get('order', 'asc') # Add order to the context
        context['consultation_type'] = self.request.GET.get('consultation_type', '') # Add consultation_type to the context
        context['search_query'] = self.request.GET.get('search_query', '') # Add search_query to the context
        
        
        
        
        
        
        
        return context

"""Custom view for handle patient consultation details in system administration"""
@login_required
def details_ptconsultation(request,id):
    
    pt_consultation = PatientConsultation.objects.get(id=id) #Ensure the consultation exists
    urgency_consultation = UrgencyConsultation.objects.select_related('consultation').filter(consultation=pt_consultation.consultation).first() # Ensure the urgency consultation exists if pt_consultion type is urgency
    common_consultation = CommonConsultation.objects.select_related('consultation').filter(consultation=pt_consultation.consultation).first()  # Ensure the common consultation exists if pt_consultion type is common
    
    if pt_consultation.consultation_type == 'urgency' and urgency_consultation:
        print(f'urgency_consultation: {urgency_consultation.main_symptom}')
    elif pt_consultation.consultation_type == 'common' and  common_consultation:
        print(f'common_consultation: {common_consultation.diagnosis}')
        
    # Get the context data and add the consultation_type to it
    context = {
        'pt_consultation': pt_consultation,
        'urgency_consultation':urgency_consultation if pt_consultation.consultation_type == 'urgency'and urgency_consultation else None,
        'common_consultation':common_consultation if pt_consultation.consultation_type == 'common' and common_consultation else None,
    }
    return render(request, 'homepage/details_ptconsultation.html', context)

"""Custom view for handle user removal in system administration"""
@login_required
def delete_ptconsultation(request,id):
    print(f"Attempting to delete consultation with ID: {id}")
    pt_consultation = get_object_or_404(PatientConsultation, id=id) #Ensure the consultation exists
    print(f'{pt_consultation.patient.user.username}')
    if request.method =='POST':
        pt_consultation.delete()
        messages.success(request,f'Consultation for {pt_consultation.patient.user.username} removed successfully 😊')
        return redirect('consultations_admin') # Redirect after successful deletion
    
    return render(request, 'homepage/delete_ptconsultation.html', {'pt_consultation': pt_consultation}) # Render a confirmation prompt to be loaded into the modal via AJAX

"""Custom view for handle patient consultations mass removal in system administration"""
@login_required
def delete_ptconsultations(request):
    if request.method == 'GET':
        pc_ids = request.GET.get('pc_ids')
        if pc_ids:
            pc_ids_list = pc_ids.split(',')
            pc_to_delete = PatientConsultation.objects.filter(id__in=pc_ids_list)
            pc_ids = ','.join(str(pc.id) for pc in pc_to_delete) #Creating a string of comma-separated user IDs
            return render(request, 'homepage/delete_ptconsultations.html', {'pt_consultations': pc_to_delete, 'pc_ids': pc_ids})
        messages.warning(request,'No Consultations IDs provided!😬')
        return redirect('consultations_admin') # Redirect to the consultations admin list page

    elif request.method == 'POST':
        pc_ids = request.POST.get('pc_ids')  # Fetch the pc_ids from the request
        
        if pc_ids:
            pc_ids_list = pc_ids.split(',')  # Split the string to get the list of IDs
            print(f'{pc_ids_list}') # Debugging purposes only
            try:
                # Convert pc IDs to integers and perform deletion
                pc_to_delete = PatientConsultation.objects.filter(id__in=pc_ids_list)
                deleted_count, _= pc_to_delete.delete()
                messages.success(request,f'{deleted_count} consultations deleted successfully😊')
                return redirect('consultations_admin') # Redirect back to consultations admin page on sucess
            except Exception as e:
                messages.warning(request,f'Error:{str(e)}🤔')
                return redirect('consultations_admin') # Redirect back to consultations admin page on error
        else:
            messages.warning(request,'No consultations IDs provided!😬')
            return redirect('consultations_admin')    # Redirect back to consultations admin page on error
    messages.warning(request,'Invalid request method!😬')
    return redirect('consultations_admin') # Redirect back to consultations admin page on error

    
    
    

