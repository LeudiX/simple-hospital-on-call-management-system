from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.urls import reverse
from .forms import RegistrationForm,ProfileForm
from .models import Doctor, Patient
from django.shortcuts import get_object_or_404
from django.contrib.auth import update_session_auth_hash

# CustomUser Views.

"""_View for register a new user in system _"""
def register(request):
    if request.method == 'POST':
        # Create a form that handle a POST request
        form =  RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            #Set the user's password securely
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            birthdate = form.cleaned_data['birthdate']
            user_type = form.cleaned_data['user_type']
            
            if password1 == password2:
                user.set_password(password1)
                user.save()
                """
                if user_type == 'patient':
                    patient = Patient.objects.create(user=user) #Fix
                elif user_type == 'doctor':
                    Doctor.objects.create(user=user) #Fix
                """
                date_output = birthdate.strftime("%Y-%m-%d")
                messages.success(request,f'Your account has been succesfully created {username},  birthdate {date_output}! Proceed to Log In')
                return redirect('login') #Redirect to the login page
            else:
                #Handling password mismatch error
                form.add_error('password2','Passwords entered do not match.Try again')
    else:
        form = RegistrationForm() # Form load for GET method
    return render(request,'users/register.html',{'form':form})

"""_Showing the current user's profile [No pk required]_"""
@login_required # Decorator to protect views that require authentication
def profile(request):
    User = get_user_model() # Retrieving the user model, ensuring compatibility with custom user models
    custom_user = User.objects.get(pk=request.user.pk) # Fetching fresh data
    if request.method =='POST':
        form = ProfileForm(request.POST,instance=request.user) # Access linked user profile
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user) # Pre-fill with current data for GET method
        age = custom_user.get_age()
    context = {
        'form':form,
        'age':age,
        'birthdate':custom_user.birthdate
        }
    return render(request,'users/profile.html',context)

@login_required
def profile_view(request):
    user = request.user
    initial_data = {}
    
    # Age Calculation process
    User = get_user_model() # Retrieving the user model, ensuring compatibility with custom user models
    age = User.objects.get(pk=request.user.pk).get_age() # Fetching AGE from CustomUser model 
    
    if user.user_type == 'doctor':
        try:
            doctor_profile = Doctor.objects.get(user=user)
            initial_data['specialty'] = doctor_profile.specialty
            initial_data['experience'] = doctor_profile.experience
        except Doctor.DoesNotExist:
            doctor_profile = None
    elif user.user_type == 'patient':
        try:
            patient_profile = Patient.objects.get(user=user)
            initial_data['address']=patient_profile.address
            initial_data['medical_history'] = patient_profile.medical_history
        except Doctor.DoesNotExist:
            patient_profile = None
            """
            try:
                common_patient  = CommonPatient.objects.get(user=user)
                initial_data['diagnosis']= common_patient.diagnosis
                initial_data['analysis_applied']= common_patient.analysis_applied
            except CommonPatient.DoesNotExist:
                common_patient = None;
            
            try:
                urgency_patient = UrgencyPatient.objects.get(user=user)
                initial_data['main_symptom'] = urgency_patient.main_symptom
                initial_data['admitted'] = urgency_patient.admitted
            except  UrgencyPatient.DoesNotExist:
                urgency_patient = None;    
            """    
        except Patient.DoesNotExist:
            patient_profile = None
    
    if request.method == 'POST':
        print(f'{request.POST}') # For debugging pourposes only
       
        patient_type = request.POST.get('patient_type')  # Get patient_type from POST data
        form = ProfileForm(request.POST, instance=user, user=user,initial=initial_data)
        
        if form.is_valid():
            form.save()
            if user.user_type == 'doctor':
                doctor_profile, created = Doctor.objects.get_or_create(user=user)
                doctor_profile.specialty = form.cleaned_data['specialty']
                doctor_profile.experience = form.cleaned_data['experience']
                doctor_profile.save()
                messages.success(request,f'Doctor {doctor_profile.user.get_full_name()} profile successfully added to registry!')
            elif user.user_type == 'patient':
                patient_profile, created = Patient.objects.get_or_create(user=user)
                patient_profile.address = form.cleaned_data['address']
                patient_profile.medical_history = form.cleaned_data['medical_history']
                patient_profile.save()
                messages.success(request,f'Patient {patient_profile.user.get_full_name()} profile successfully added to registry!')
                """
                print(f'Patient profile: {patient_profile.patient_type}')
                if patient_profile.patient_type =='common':
                    common_patient,created = CommonPatient.objects.get_or_create(user=user)
                    common_patient.diagnosis = form.cleaned_data['diagnosis']
                    common_patient.analysis_applied = form.cleaned_data['analysis_applied']
                    common_patient.save()
                    messages.success(request,f'Patient {common_patient.user.get_full_name()} with {common_patient.patient_type} profile successfully added to registry!')
                
                elif patient_profile.patient_type == 'urgency':
                    urgency_patient, created = UrgencyPatient.objects.get_or_create(user=user)
                    urgency_patient.main_symptom = form.cleaned_data['main_symptom']
                    urgency_patient.admitted = form.cleaned_data['admitted']
                    urgency_patient.save()
                    messages.success(request,f'Patient {urgency_patient.user.get_full_name()}  with {urgency_patient.patient_type} profile successfully added to registry!')
                """
            return redirect('profile') 
    else:
        form = ProfileForm(instance=user, user=user,initial=initial_data)
        
    context = {
        'form':form,
        'age':age,
        'doctor':doctor_profile if user.user_type == 'doctor' else None, #Accessing current doctor info if present in session
        'patient': patient_profile if user.user_type == 'patient' else None, #Accessing current patient info if present in session
        }
    
    return render(request, 'users/profile.html',context)
 