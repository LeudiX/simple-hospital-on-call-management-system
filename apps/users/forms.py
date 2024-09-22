from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth import password_validation
from .models import CustomUser, Doctor, Patient
from django.core.validators import MinValueValidator,MaxValueValidator

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
        fields = ('username','first_name','last_name', 'email','user_type','birthdate','gender') # Fields to edit

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("email",) #Field to edit in django admin

# Update Profile form
class ProfileForm(forms.ModelForm):
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
            
            self.fields['specialty'] = forms.ChoiceField(choices=Doctor.SPECIALTIES)
            self.fields['experience'] = forms.IntegerField(min_value=0, max_value=50)

        elif user and user.user_type == 'patient':
            self.fields['patient_type'] = forms.ChoiceField(choices=Patient.PATIENT_TYPE_CHOICES)
            self.fields['temperature'] = forms.DecimalField(max_digits=5,decimal_places=2)
            self.fields['pulse'] = forms.IntegerField(validators=[MinValueValidator(40),MaxValueValidator(120)])
            self.fields['systolic_pressure'] = forms.DecimalField(max_digits=5,decimal_places=2)
            self.fields['diastolic_pressure'] = forms.DecimalField(max_digits=5,decimal_places=2)
            
    def clean_experience(self):
        experience = self.cleaned_data.get('experience')
        if experience is None:
            raise forms.ValidationError("Experience is required.")
        return experience    