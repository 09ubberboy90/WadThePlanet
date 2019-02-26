from django import forms
from django.forms import ModelForm
from planet.models import *
from crispy_forms.helper import FormHelper
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(forms.ModelForm):
    password_copy = forms.CharField(
        label='Confirm password')

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = PlanetUser.objects.filter(username=username)
        if r.count():
            raise ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = PlanetUser.objects.filter(email=email)
        if r.count():
            raise ValidationError("Email already exists")
        return email

    def clean_password_copy(self):
        password = self.cleaned_data.get('password')
        password_copy = self.cleaned_data.get('password_copy')

        if password and password_copy and password != password_copy:
            raise ValidationError("Password don't match")

        return password_copy

    def save(self, commit=True):
        user = PlanetUser.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password'],
            self.cleaned_data['avatar']
        )
        return user

    class Meta:
        model = PlanetUser
        fields = ['username', 'password', 'email', 'avatar']

        def __init__(self, *args, **kwargs):
            super(UserForm, self).__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.form_id = 'UserForm'
            self.helper.form_class = 'form-control is-valid'
            self.helper.form_method = 'post'
            self.helper.form_action = 'submit_survey'
