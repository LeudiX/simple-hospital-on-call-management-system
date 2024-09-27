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

    user_type = forms.ChoiceField(choices=[('','Choose user role')]+list(CustomUser.USER_TYPE_CHOICES),required=True)    
    
    gender = forms.ChoiceField(choices=[('','Choose your gender')]+list(CustomUser.GENDER_CHOICES),required=True)    
        
    class Meta:
        model = CustomUser
        fields = ('username','first_name','last_name', 'email','user_type','birthdate','gender') # Fields to edit

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("email",) #Field to edit in django admin

# Update Profile form
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
        data = kwargs.get('data', None)  # Get form data from POST request
        initial_patient_type = kwargs.get('initial', {}).get('patient_type')  # Get patient_type from initial data  
        patient_type = data.get('patient_type') if data else initial_patient_type  # Use POST data if available, otherwise use initial data
        super(ProfileForm, self).__init__(*args, **kwargs)

        if user and user.user_type == 'doctor':
            # Modified the specialty field to show "Choose a patient"(Casting to list to avoid tuples concatenation problem )
            self.fields['specialty'] = forms.ChoiceField(choices=[('','Choose your specialty')]+ list(Doctor.SPECIALTIES),required=True)
            self.fields['experience'] = forms.IntegerField(min_value=0, max_value=50)

        elif user and user.user_type == 'patient':
            self.fields['address'] = forms.CharField(max_length=125,help_text='Your address info')
            self.fields['medical_history'] = forms.CharField( widget=forms.Textarea, required=True, error_messages={'required': 'Please provide medical history.'}) # Custom error message
    
            """_summary_
            
            # Always add fields for both common and urgency patients
            if patient_type =='common':
                self.add_common_patient_fields()
            elif patient_type =='urgency':
                self.add_urgency_patient_fields()
            
            if 'diagnosis' in self.fields:
                # Adding class to label via help_text (hack to target label via JavaScript)
                #self.fields['diagnosis'].help_text = 'common-fields-label'
                self.fields['diagnosis'].widget.attrs.update({'class': 'common-fields'})
            if 'analysis_applied' in self.fields:
                self.fields['analysis_applied'].widget.attrs.update({'class': 'common-fields'})

            if 'main_symptom' in self.fields:
                self.fields['main_symptom'].widget.attrs.update({'class': 'urgency-fields'})
            if 'admitted' in self.fields:
                self.fields['admitted'].widget.attrs.update({'class': 'urgency-fields'})
                
                
             def add_common_patient_fields(self):
        Add fields specific to CommonPatient.
        self.fields['diagnosis'] = forms.CharField(max_length=255, required=True)
        self.fields['analysis_applied'] = forms.ChoiceField(choices=[('','Was analysis applied?')]+ list(CommonPatient.ANALYSIS_CHOICES), required=True)
        
            def add_urgency_patient_fields(self):
        Add fields specific to UrgencyPatient.
        self.fields['main_symptom'] = forms.CharField(max_length=255, required=True)
        self.fields['admitted'] = forms.ChoiceField(choices=[('','Was patient admitted to the center?')]+ list(UrgencyPatient.ADMISSION_CHOICES), required=True)
        """
            # Add CSS classes to dynamically hide/show fields
            # Apply 'common-fields' class to both label and widget for common fields
            
 
    """NOT WORKING RIGHT NOW"""
    def clean_experience(self):
        experience = self.cleaned_data['experience']
        if experience is None:
            raise forms.ValidationError("Experience is required.")
        return experience
    