from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.template import RequestContext
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
    user = request.user.socialuser
    # form = BrotifyProfileForm(instance=user)
    form = SocialUser.objects.get(user=request.user)

    if request.method == 'POST':
        user_form = BrotifyProfileForm(request.POST, request.FILES, instance=user)
        profile_form = BrotifyUserCreationForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            form.save()
            SocialUser.objects.create(**{'user': user})

    context = {'form': form}
    return render(request, 'profile.html', context)


def login_user(request):
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
    return render('login.html')

