from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm,ProfileForm
from .models import CustomUser
from django.shortcuts import get_object_or_404

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
                messages.success(request,f'Your account has been succesfully created {username} at {date_output}! Proceed to Log In')
                return redirect('login') #Redirect to the login page
            else:
                #Handling password mismatch error
                form.add_error('password2','Passwords entered do not match.Try again')
    else:
        form = RegistrationForm()
    return render(request,'users/register.html',{'form':form})

@login_required
def profile(request,pk):
    
    custom_user = get_object_or_404(CustomUser,pk=pk)
    if request.method =='POST':
        form = ProfileForm(request.POST,instance=request.user) # Access linked user profile
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user) # Pre-fill with current data
        age = custom_user.get_age()
    context = {
        'form':form,
        'age':age,
        'birthdate':custom_user.birth_date
        }
    return render(request,'users/profile.html',context)