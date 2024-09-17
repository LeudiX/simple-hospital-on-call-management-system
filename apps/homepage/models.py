from django.utils import timezone
from django.db import models
from django.forms import ValidationError
from apps.users.models import Doctor,Patient

# Consultations model
class Consultation(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='consultations_doctor') #One to many 
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations_patient')
    consultation_date = models.DateTimeField(default=timezone.now().date())
    notes = models.TextField(max_length=200,blank=True, null=True)  # Optional notes field

    def __str__(self):
        return f"Consultation with {self.doctor} on {self.consultation_date.strftime('%Y-%m-%d')}"
    
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
        
        """_TODO_
        
        WARNINGS:
        homepage.Consultation.consultation_date: (fields.W161) Fixed default value provided.
        HINT: It seems you set a fixed date / time / datetime value as default for this field. 
        This may not be what you want. If you want to have the current date as default, use `django.utils.timezone.now`
        """