from django.utils import timezone
from django.db import models
from django.forms import ValidationError
from apps.users.models import Doctor,Patient

# Consultations model
class Consultation(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='consultations_doctor') #One to many 
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations_patient')
    
    #Solved issue with timezone.now and migrations mistake reboot every time. Also when i create and object of this type
    consultation_date = models.DateTimeField(default=timezone.now) 
    notes = models.TextField(max_length=200,blank=True, null=True)  # Optional notes field

    def __str__(self):
        return f"Doctor: {self.doctor.first_name} in consultation with {self.patient.first_name} on {self.consultation_date.strftime('%Y-%m-%d')}"
    
    class Meta:
        verbose_name = "Consultation"
        verbose_name_plural = "Consultations"
        
        constraints = [
            models.UniqueConstraint(fields=['doctor', 'patient', 'consultation_date'], name='unique_consultation')
        ]

    def clean(self):
        # Add custom validation here if needed, e.g., to prevent scheduling
        # consultations in the past or overlapping appointments.
        if self.consultation_date < timezone.now():
            raise ValidationError("Consultation date cannot be in the past.")
        
        # Check for overlapping appointments for the doctor
        overlapping_appointments = Consultation.objects.filter(
            doctor=self.doctor,
            consultation_date__range=(
                self.consultation_date,
                self.consultation_date + timezone.timedelta(minutes=30)  # Assuming 30-minute appointments
            )
        ).exclude(pk=self.pk if self.pk else None)  # Exclude the current appointment if editing

        if overlapping_appointments.exists():
            raise ValidationError(f"Dr. {self.doctor} already has an appointment scheduled for this time.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Run model validation before saving
        super().save(*args, **kwargs)
    