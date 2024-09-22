from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div,Layout, Submit

from .models import Consultation
from apps.users.models import Doctor, Patient

class ConsultationForm(forms.ModelForm):
   
    """"
    patient_name = forms.ModelChoiceField(
        label='Patient',
        help_text='Select the patient',
        required =True,
        queryset= Patient.objects.filter(user_type='patient'),
        empty_label="Nothing here"
        )
    """
    class Meta:
        model = Consultation
        fields = ['patient', 'doctor', 'consultation_date', 'notes']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ConsultationForm, self).__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.filter(username='Titongo')
        self.fields['doctor'] = forms.ModelChoiceField(
            queryset=Doctor.objects.filter(id=user.id), 
            initial=user.id, widget=forms.HiddenInput()) 
    