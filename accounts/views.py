from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView
from accounts.forms import BrotifyUserCreationForm, BrotifyProfileForm
from accounts.models import SocialUser
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render


class SignUp(CreateView):
    form_class = BrotifyUserCreationForm
    # Reverse_lazy because for all generic class-based views the urls are not loaded when the file is imported
    # So we have to use the lazy form of reverse to load them later when they're available
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


class UserLogin(LoginView):
    template_name = 'login.html'


@login_required
def index(request):

    try:
        social_user = request.user.socialuser
    except SocialUser.DoesNotExist:
        SocialUser.objects.create(**{'user': request.user})
        social_user = request.user.socialuser

    user_form = BrotifyProfileForm(request.POST, request.FILES, instance=social_user)

    if request.method == 'POST':
        if user_form.is_valid():
            user_form.save()

    context = {'form': user_form}
    return render(request, 'profile.html', context)


def login_user(request):
    logout(request)
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
    return render('login.html')
