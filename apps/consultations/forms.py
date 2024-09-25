from django.utils import timezone
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div,Layout, Submit

from .models import Consultation
from apps.users.models import Doctor, Patient

class ConsultationForm(forms.ModelForm):
   
        
    def __init__(self, *args, **kwargs):
        
       # Call the parent class's __init__ method
        super().__init__(*args, **kwargs)
        
        # Modify the patient field to show "Choose a patient"
        self.fields['patient'].empty_label = "Choose a patient"
        self.fields['patient'].queryset = self.get_available_patients()

        # Plan A for notes validation
        self.fields['notes'] = forms.CharField( widget=forms.Textarea, required=True, error_messages={'required': 'Please provide your notes.'}) # Custom error message
    
    class Meta:
        model = Consultation
        fields = ['patient', 'notes']
    
    """_ Getting the list of patients who have not been consulted within the last 30 minutes_ [NOT WORKING RIGHT NOW]
    """
    def get_available_patients(self):
        recent_patient_ids = Consultation.objects.filter(
            consultation_date__gte=timezone.now() - timezone.timedelta(minutes=30)
        ).values_list('patient_id', flat=True)
        print(f'{recent_patient_ids}')  #Debugging porposes only
        return Patient.objects.exclude(user__id__in=recent_patient_ids)

    # Plan B for notes validation
    """_Overriding form clean method for in order to handle validation error and avoid saving the consultation_[OPTIONAL]
    """
    def clean_notes(self):
        data = self.cleaned_data['notes']
        if not data.strip():
            raise forms.ValidationError("Notes cannot be empty or just whitespace.")
        return data