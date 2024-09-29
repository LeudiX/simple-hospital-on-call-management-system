from django.contrib import admin
from .models import Consultation,PatientConsultation,CommonConsultation,UrgencyConsultation,VitalSigns
# Register your models here.
admin.site.register(Consultation)
admin.site.register(PatientConsultation)
admin.site.register(VitalSigns)
admin.site.register(UrgencyConsultation)
admin.site.register(CommonConsultation)