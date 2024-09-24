from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div,Layout, Submit

from .models import Consultation
from apps.users.models import Doctor, Patient

class ConsultationForm(forms.ModelForm):
   
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.all(),
        help_text='Choose the patient',
        )
    notes  = forms.Textarea(attrs={'placeholder':'Patient treatment'})
   
    class Meta:
        model = Consultation
        fields = ['patient', 'doctor', 'consultation_date', 'notes']
     
    def clean_notes(self):
        notes = self.cleaned_data.get('notes')
        if notes is None:
            raise forms.ValidationError("Notes is required.")
        return notes
    