from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from .models import CustomUser

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
    

    
    class Meta:
        model = CustomUser
        fields = ('username', 'email','user_type','birthdate','gender') 