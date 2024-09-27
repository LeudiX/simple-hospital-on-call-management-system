from django.utils import timezone
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Submit

from .models import CommonConsultation, Consultation, PatientConsultation, UrgencyConsultation, VitalSigns


class ConsultationForm(forms.ModelForm):
    
    class Meta:
        model = Consultation
        fields = ['notes']
    
    def __init__(self, *args, **kwargs):
        
       # Call the parent class's __init__ method
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Consultation',
                Field('notes')
            )
        )
        
        # Plan A for notes validation
        #self.fields['notes'] = forms.CharField( widget=forms.Textarea, required=True, error_messages={'required': 'Please provide your notes.'}) # Custom error message

    # Plan B for notes validation
    """_Overriding form clean method for in order to handle validation error and avoid saving the consultation_[OPTIONAL]
    """
    def clean_notes(self):
        data = self.cleaned_data['notes']
        if not data.strip():
            raise forms.ValidationError("Notes cannot be empty or just whitespace.")
        return data

class UrgencyConsultationForm(forms.ModelForm):
    class Meta:
        model = UrgencyConsultation
        fields = ('main_symptom', 'admitted')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Urgency Consultation',
                Field('main_symptom'),
                Field('admitted')
            )
        )

class CommonConsultationForm(forms.ModelForm):
    class Meta:
        model = CommonConsultation
        fields = ('diagnosis', 'test_applied')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Common Consultation',
                Field('diagnosis'),
                Field('test_applied')
            )
        )

class PatientConsultationForm(forms.ModelForm):
    class Meta:
        model = PatientConsultation
        fields = ('patient','consultation_type',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Patient Consultation',
                Field('patient'),
                Field('consultation_type')
            )
        )

class VitalSignsForm(forms.ModelForm):
    class Meta:
        model = VitalSigns
        fields = ('temperature', 'pulse', 'diastolic_pressure', 'systolic_pressure')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Vital Signs',
                Field('temperature'),
                Field('pulse'),
                Field('diastolic_pressure'),
                Field('systolic_pressure')
            )
        )