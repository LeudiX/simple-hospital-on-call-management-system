from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from apps.consultations.models import PatientConsultation, VitalSigns
from .forms import RegistrationForm,ProfileForm,CustomUserChangeForm
from .models import CustomUser,Doctor, Patient
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger




"""_Custom view for register a new user in system _"""
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
            
            if password1 == password2:
                user.set_password(password1)
                user.save()
                date_output = birthdate.strftime("%Y-%m-%d")
                messages.success(request,f'Your account has been succesfully created {username},  birthdate {date_output}! Proceed to Log In😊')
                return redirect('login') #Redirect to the login page
            else:
                #Handling password mismatch error
                form.add_error('password2','Passwords entered do not match.Try again')
    else:
        form = RegistrationForm() # Form load for GET method
    return render(request,'users/register.html',{'form':form})

"""Custom view for handle users profiles in system"""
@login_required
def profile_view(request):
    user = request.user
    initial_data = {}
    
    # Age Calculation process
    User = get_user_model() # Retrieving the user model, ensuring compatibility with custom user models
    age = User.objects.get(pk=request.user.pk).get_age() # Fetching AGE from CustomUser model 
    
    # Get the current doctor from the request (assuming you have access to it)
    if user.user_type == 'doctor':
        try:
            doctor_profile = Doctor.objects.get(user=user)
            initial_data['specialty'] = doctor_profile.specialty
            initial_data['experience'] = doctor_profile.experience
        except Doctor.DoesNotExist:
            doctor_profile = None
    elif user.user_type == 'patient':
        try:
            # Get the current patient from the request (assuming you have access to it)
            patient_profile = Patient.objects.get(user=user)
            
            # Query all consultations for the patient ordered by consultation_date
            last_consultation = PatientConsultation.objects.filter(patient=patient_profile).order_by('-consultation__consultation_date').first()
            
            # Get the last VitalSign entry related to the last consultation
            last_vital_signs = None
            if last_consultation:
                last_vital_signs = VitalSigns.objects.filter(consultation= last_consultation.consultation).first()
            
            initial_data['address']=patient_profile.address
            initial_data['medical_history'] = patient_profile.medical_history    
        except Patient.DoesNotExist:
            patient_profile = None
            # Handle the case where the patient has no consultations.
            last_consultation = None
            last_vital_signs = None
    
    if request.method == 'POST':
       
        form = ProfileForm(request.POST, instance=user, user=user,initial=initial_data)
        
        if form.is_valid():
            form.save()
            if user.user_type == 'doctor':
                doctor_profile, created = Doctor.objects.get_or_create(user=user)
                doctor_profile.specialty = form.cleaned_data['specialty']
                doctor_profile.experience = form.cleaned_data['experience']
                doctor_profile.save()
                messages.success(request,f'Doctor {doctor_profile.user.get_full_name()} profile successfully updated in registry!😊')
            elif user.user_type == 'patient':
                patient_profile, created = Patient.objects.get_or_create(user=user)
                patient_profile.address = form.cleaned_data['address']
                patient_profile.medical_history = form.cleaned_data['medical_history']
                patient_profile.save()
                messages.success(request,f'Patient {patient_profile.user.get_full_name()} profile successfully updated in registry!😊')
            return redirect('profile') 
    else:
        form = ProfileForm(instance=user, user=user,initial=initial_data)
        
    context = {
        'form':form,
        'age':age,
        'doctor':doctor_profile if user.user_type == 'doctor' else None, #Accessing current doctor info if present in session
        'patient': patient_profile if user.user_type == 'patient' else None, #Accessing current patient info if present in session
        'last_consultation': last_consultation if user.user_type == 'patient' and last_consultation else None,
        'last_vital_signs': last_vital_signs if user.user_type == 'patient' and last_vital_signs else None,
        }   
    
    if user.user_type == 'patient' and not last_consultation:
        context['no_consultations'] = True
    
    return render(request, 'users/profile.html',context)

"""Custom view for list users in system administration"""
@login_required
def list_users(request):
    
    # Get search query
    search_query =  request.GET.get('search','')  
    
    # Fetch and sort users by username
    # Excluding superusers by filtering out users where is_superuser is True
    users = CustomUser.objects.all().exclude(is_superuser=True)
    
    # Search users by username
    if search_query:
        users = users.filter(username__icontains=search_query)
        print(f'{users}')
        
    # Filter by user type only if provided and not 'None'
    user_type = request.GET.get('user_type')
    if user_type and user_type!=None:
        users = users.filter(user_type=user_type)
        print(f'{users}')

    # Define allowed sort fields
    allowed_sort_fields = ['username', 'birthdate','date_joined']
    # Get sorting parameters and validate
    sort_by = request.GET.get('sort') or 'username'  # Default to 'username' if empty
    order = request.GET.get('order') or 'asc'          # Default to ascending order if empty
    
    if sort_by not in allowed_sort_fields:
        sort_by = 'username'  # Fallback to default if invalid
    sort_field = f"-{sort_by}" if order=='desc' else sort_by
    
    # Apply sorting to users
    users = users.order_by(sort_field)
    
    # Calculate and include age for all the users in system
    users_age = [{'user': user,'age': user.get_age()} for user in users]
    
    # Pagination settings 
    page = request.GET.get('page',1)
    paginator = Paginator(users_age,4) # 4 users per page by now
    
    try:
        paginated_users = paginator.page(page)
    except PageNotAnInteger:
        paginated_users = paginator.page(1)
    except EmptyPage:
        paginated_users = paginator.page(paginator.num_pages)
        
    # Add search query, filtering and order to the template context
    context = {
        'users':paginated_users,
        'order':order,
        'user_type':user_type,  
        'search_query':search_query,
        'sort_by':sort_by
    }
        
    return render(request,'users/list_users.html',context)

"""Custom view for handle users edition in system administration"""
@login_required
def edit_user(request,id):
    user = get_object_or_404(CustomUser, id=id) # Ensure the user exists
    
    if request.method == 'POST':       
        form = CustomUserChangeForm(request.POST,instance=user)
        if form.is_valid():
           form.save()
           messages.success(request,f'User {user.username} updated successfully😊')
           return redirect('users')
        else:
            return messages.warning(request,f'Errors updating {user.username} : {form.errors}🤔')   
    else:
        form = CustomUserChangeForm(instance=user)
        
    context = {
        'form':form, # Sending the form data and values to context
        'user':user # Sending the user instance to context
    }

    return render(request,'users/update_user_form.html',context)

"""Custom view for handle user removal in system administration"""
@login_required
def delete_user(request,id):
    user = get_object_or_404(CustomUser,id=id) # Ensure the user exists
    
    if request.method =='POST':
        user.delete()
        messages.success(request,f'User {user.username} removed successfully 😊')
        return redirect('users') # Redirect after successful deletion
    return render(request, 'users/delete_user_confirm.html', {'user': user}) # Render a confirmation prompt to be loaded into the modal via AJAX

"""Custom view for handle mass users removal in system administration"""
@login_required
def delete_users(request):
    if request.method == 'GET':
        user_ids = request.GET.get('user_ids')
        if user_ids:
            user_ids_list = user_ids.split(',')
            users_to_delete = CustomUser.objects.filter(id__in=user_ids_list)
            user_ids = ','.join(str(user.id) for user in users_to_delete) #Creating a string of comma-separated user IDs
            return render(request, 'users/delete_users_confirm.html', {'users': users_to_delete, 'user_ids': user_ids})
        messages.warning(request,'No users IDs provided!😬')
        return redirect('users')

    elif request.method == 'POST':
        user_ids = request.POST.get('user_ids')  # Fetch the user_ids from the request
        
        if user_ids:
            user_ids_list = user_ids.split(',')  # Split the string to get the list of IDs
            print(f'{user_ids_list}') # Debugging purposes only
            try:
                # Convert user IDs to integers and perform deletion
                users_to_delete = CustomUser.objects.filter(id__in=user_ids_list)
                deleted_count, _= users_to_delete.delete()
                messages.success(request,f'{deleted_count} users deleted successfully😊')
                return redirect('users') # Redirect back to users listing page on sucess
            except Exception as e:
                messages.warning(request,f'Error:{str(e)}🤔')
                return redirect('users') # Redirect back to users page on error
        else:
            messages.warning(request,'No users IDs provided!😬')
            return redirect('users')    # Redirect back to users page on error
    messages.error(request,'Invalid request method!😬')
    return redirect('users') # Redirect back to users page on error
    
   