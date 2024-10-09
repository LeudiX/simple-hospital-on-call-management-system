from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.forms import ValidationError
from apps.users.models import Doctor,Patient
from django.core.validators import MinValueValidator,MaxValueValidator

# Consultations model
class Consultation(models.Model):
    
    # Offset calcultations between me local timezone and the server timezone (6h difference)
    offset = timedelta(hours=6)
    
    CONSULTATION_STATUS = (
        ('scheduled','Scheduled'),
        ('in-progress','In-progress'),
        ('completed','Completed'),
    )  
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='consultations_doctor') #One to many 
    #Solved issue with timezone.now and migrations mistake reboot every time. Also when i create and object of this type
    #Added offset variable for local timezone calculation 
    consultation_date = models.DateTimeField(default=timezone.now()-offset,help_text="Consultation current time") 
    notes = models.TextField(max_length=200,blank=True, null=True)  # Optional notes field
    status = models.CharField(max_length=20, choices=CONSULTATION_STATUS)  # Choices can be added here.
       
    def __str__(self):
        return f"Doctor: {self.doctor.user.first_name} in consultation on {self.consultation_date.strftime('%Y-%m-%d')}"
    
    # Displaying the patient's name directly in the consultation list without the extra loop
    def get_patient_names(self):
        return ', '.join([pc.patient.user.get_full_name() for pc in self.patientconsultation_set.all()])
    
    # Displaying the consultation_type name directly in the consultation list without the extra loop
    def get_consultation_type(self):
        return ', '.join([pc.consultation_type for pc in self.patientconsultation_set.all()])
    
    class Meta:
        verbose_name = "Consultation"
        verbose_name_plural = "Consultations"
        
        constraints = [
            # Each doctor can only has one consultation at the time 
            models.UniqueConstraint(fields=['doctor', 'consultation_date'], name='unique_consultation')
        ]

class UrgencyConsultation(models.Model):
    
    NO=0
    YES=1
    
    ADMISSION_CHOICES=(
        (NO,'No'),
        (YES,'Yes')
    ) 
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE)
    main_symptom = models.CharField(max_length=255,verbose_name='Main synptom',help_text="Patient's main symptom")
    admitted =models.IntegerField(verbose_name='Admitted', choices=ADMISSION_CHOICES, help_text="Patient's required admission?",null=True,blank=True)

class CommonConsultation(models.Model):
    
    NO=0
    YES=1
    
    TEST_CHOICES=(
        (NO,'No'),
        (YES,'Yes')
    )
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE)
    diagnosis=models.CharField(max_length=255,verbose_name='Diagnosis',help_text="Patient's medical diagnosis",null=True,blank=True)
    test_applied=models.IntegerField(verbose_name='Analysis applied', choices=TEST_CHOICES, help_text="Patient's required tests?",null=True,blank=True)
     
class PatientConsultation(models.Model):
    CONSULTATION_TYPE_CHOICES = (
        ('urgency', 'Urgency'),
        ('common', 'Common'),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    consultation_type = models.CharField(max_length=20, choices=CONSULTATION_TYPE_CHOICES)
     
class VitalSigns(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)   
    # Temperature in degrees Celsius
    temperature = models.DecimalField(
                                    max_digits=5,
                                    decimal_places=2,
                                    validators=[MinValueValidator(36.5),MaxValueValidator(42.5)],
                                    verbose_name='Body temperature',
                                    help_text="Patient's body temperature in degrees Celsius",
                                    error_messages='Please, select a value between 36.5 and 42.5',
                                    null=True,   # Allows the field to be null if temperature is unknown
                                    blank=True)  # Allows the field to be blank in forms 

    # Pulse in beats per minute    
    pulse = models.IntegerField(
        validators=[MinValueValidator(40),MaxValueValidator(120)],
        verbose_name='Pulse Rate',
        help_text="Patient's pulse rate in beats per minute",
        error_messages='Please, select a value between 40 and 120',
        null=True,  # Allows the field to be null if pulse is unknown
        blank=True) # Allows the field to be blank in forms 
    
    # Blood pressure in mmHg, typically recorded as systolic(HIGH)/diastolic(LOW)
    systolic_pressure = models.DecimalField(
        verbose_name="Systolic Blood Pressure",
        help_text="Patient's systolic blood pressure in mmHg",
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(90),MaxValueValidator(140)],
        error_messages='Please, select a value between 90 and 140',
        null=True,  # Allows the field to be null if blood pressure is unknown
        blank=True,  # Allows the field to be blank in forms
    )
    diastolic_pressure = models.DecimalField(
        verbose_name="Diastolic Blood Pressure",
        help_text="Patient's diastolic blood pressure in mmHg",
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(60),MaxValueValidator(90)],
        error_messages='Please, select a value between 60 and 90',
        null=True,  # Allows the field to be null if blood pressure is unknown
        blank=True,  # Allows the field to be blank in forms
    )
      
    """_Returns a summary of the patient's vital signs. This promotes encapsulation by providing a 
        clear interface to access the vital signs_
    """
    def get_vital_signs(self):
        # Returns a summary of the patient's vital signs
        return f"Temperature: {self.temperature}, Pulse: {self.pulse}, Blood Pressure: {self.systolic_pressure}/{self.diastolic_pressure}"
