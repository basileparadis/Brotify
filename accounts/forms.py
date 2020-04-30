from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from accounts.models import SocialUser


class SocialUserCreationForm(UserCreationForm):
    '''
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    prenom = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom', }))
    nom = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de famille', }))
    courriel = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Courriel', }))
    avatar = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Avatar', }))
    '''

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'email']
