from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView


class home_page(TemplateView):
    template_name = 'homepage/home.html'

