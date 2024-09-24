from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.forms import ValidationError
from apps.users.models import Doctor,Patient

# Consultations model
class Consultation(models.Model):
    
    # Offset calcultations between me local timezone and the server timezone (6h difference)
    offset = timedelta(hours=6)
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='consultations_doctor',help_text="Doctor's name") #One to many 
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations_patient')
    
    #Solved issue with timezone.now and migrations mistake reboot every time. Also when i create and object of this type
    #Added offset variable for local timezone calculation 
    consultation_date = models.DateTimeField(default=timezone.now()-offset,help_text="Consultation current time") 
    notes = models.TextField(max_length=200,blank=True, null=True)  # Optional notes field

    def __str__(self):
        return f"Doctor: {self.doctor.user.first_name} in consultation with {self.patient.user.first_name} on {self.consultation_date.strftime('%Y-%m-%d')}"
    
    class Meta:
        verbose_name = "Consultation"
        verbose_name_plural = "Consultations"
        
        constraints = [
            models.UniqueConstraint(fields=['doctor', 'patient', 'consultation_date'], name='unique_consultation')
        ]

    def clean(self):
        offset = timedelta(hours=6)
        # Adding custom validation here if needed, e.g., to prevent scheduling
        # consultations in the past or overlapping appointments.
        if self.consultation_date < timezone.now()-offset:
            
            #print(f'Current timezone: {timezone.now()}')
            #print(f'Current consultation_date: {self.consultation_date}')
            raise ValidationError("Consultation date cannot be in the past.")
        
        # Check for overlapping appointments for the doctor
        overlapping_appointments = Consultation.objects.filter(
            doctor=self.doctor,
            consultation_date__range=(
                self.consultation_date,
                self.consultation_date + timezone.timedelta(minutes=20)  # Assuming 20-minute appointments
            )
        ).exclude(pk=self.pk if self.pk else None)  # Exclude the current appointment if editing

        print(f'Overlapping appointments: {overlapping_appointments}')
        if overlapping_appointments.exists():
            raise ValidationError(f"Dr.{self.doctor.user.first_name} already has an appointment scheduled for this time. Wait 20 mins")

    def save(self, *args, **kwargs):
        self.full_clean()  # Run model validation before saving
        super().save(*args, **kwargs)
    