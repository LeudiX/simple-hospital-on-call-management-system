from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth import password_validation
from .models import CustomUser, Doctor, Patient
from django.core.validators import MinValueValidator,MaxValueValidator

"""User's registry form"""
class RegistrationForm(UserCreationForm):
    
    email = forms.EmailField(required=True,widget=forms.EmailInput(attrs={'class':'form-control'}))
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class':'form-control','id':'password-input'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
    )
    
    #Adding and addditional field for password strength checking
    password_strength = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )
    
    birthdate = forms.DateField(
        required=True,
        label='Birthdate',
        widget=forms.DateInput(attrs={'class':'datepicker','type':'date'}),
        )

    user_type = forms.ChoiceField(choices=[('','Choose user role')]+list(CustomUser.USER_TYPE_CHOICES),required=True)    
    
    gender = forms.ChoiceField(choices=[('','Choose your gender')]+list(CustomUser.GENDER_CHOICES),required=True)    
        
    class Meta:
        model = CustomUser
        fields = ('username','first_name','last_name', 'email','user_type','birthdate','gender') # Fields to edit

"""User's update form (ADMIN Tasks)"""
class CustomUserChangeForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ('username','email','user_type','is_active') 

"User's personal profile form"
class ProfileForm(forms.ModelForm):
    
    gender = forms.ChoiceField(choices=[('','Choose your gender')]+list(CustomUser.GENDER_CHOICES),required=True)    
    
    class Meta:
        model = CustomUser
        fields = ['username','first_name','last_name', 'email','birthdate','gender'] # Fields to edit
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}), # Improved date picker
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
    
        super(ProfileForm, self).__init__(*args, **kwargs)

        if user and user.user_type == 'doctor':
            # Modified the specialty field to show "Choose a patient"(Casting to list to avoid tuples concatenation problem )
            self.fields['specialty'] = forms.ChoiceField(choices=[('','Choose your specialty')]+ list(Doctor.SPECIALTIES),required=True)
            self.fields['experience'] = forms.IntegerField(min_value=0, max_value=50)

        elif user and user.user_type == 'patient':
            self.fields['address'] = forms.CharField(max_length=125,help_text='Your address info')
            self.fields['medical_history'] = forms.CharField( widget=forms.Textarea, required=True, error_messages={'required': 'Please provide medical history.'}) # Custom error message

    