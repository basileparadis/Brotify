from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from accounts.forms import BrotifyUserCreationForm


class SignUp(CreateView):
    form_class = BrotifyUserCreationForm
    # Reverse_lazy because for all generic class-based views the urls are not loaded when the file is imported
    # So we have to use the lazy form of reverse to load them later when they're available
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


@login_required
def index(request):
    return render(request, 'profile.html')
