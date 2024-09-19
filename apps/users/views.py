from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.urls import reverse
from .forms import RegistrationForm,ProfileForm
from .models import CustomUser
from django.shortcuts import get_object_or_404
from django.contrib.auth import update_session_auth_hash

# CustomUser Views.
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
                messages.success(request,f'Your account has been succesfully created {username},  birthdate {date_output}! Proceed to Log In')
                return redirect('login') #Redirect to the login page
            else:
                #Handling password mismatch error
                form.add_error('password2','Passwords entered do not match.Try again')
    else:
        form = RegistrationForm()
    return render(request,'users/register.html',{'form':form})

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