import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from apps.consultations.models import Consultation
from apps.users.models import CustomUser, Doctor, Patient
from .forms import ConsultationForm
from django.contrib.auth import get_user_model

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView

# Consultations views.
class home_page(TemplateView):
    template_name = 'homepage/home.html'

"""
@login_required
def consultation_register(request):
   
    if request.method == 'POST': 
        form = ConsultationForm(request.POST,instance=request.user) # Access linked user profile
        if form.is_valid():
            consultation = form.save(commit=False)
            patient = CustomUser.objects.filter(user_type='patient')
            doctor = form.cleaned_data['doctor']  
            consultation.save()
            messages.success(request,f'Your consultation has been succesfully created Ms. {doctor}!')
            return redirect('consultations')
    else:
        form = ConsultationForm(instance =request.user)
    context = {
            'form':form
        }
    return render(request,'homepage/consultations.html',context)

"""
class CreateConsultationView(LoginRequiredMixin, CreateView):
    model = Consultation
    form_class = ConsultationForm
    template_name = 'homepage/consultations.html'
    success_url = '/consultations/'

    def form_valid(self, form):
        # Assign the current doctor to the consultation
        form.instance.doctor = self.request.user
        form.instance.consultation_date = datetime.timezone.now()  # Set the current date
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = Patient.objects.all()  # Get all patients
        return context

