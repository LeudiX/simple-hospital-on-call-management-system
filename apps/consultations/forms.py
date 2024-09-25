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
    
    
    """_ Getting the list of patients who have not been consulted within the last 30 minutes_
    """
    def get_available_patients(self):
        recent_patient_ids = Consultation.objects.filter(
            consultation_date__gte=timezone.now() - timezone.timedelta(minutes=30)
        ).values_list('patient_id', flat=True)
        print(f'{recent_patient_ids}')  #Debugging porposes only
        return Patient.objects.exclude(user__id__in=recent_patient_ids)
         
    def clean_notes(self):
        notes = self.cleaned_data.get('notes')
        if notes is None:
            raise forms.ValidationError("Notes is required.")
        return notes
    
    class Meta:
        model = Consultation
        fields = ['patient', 'notes']