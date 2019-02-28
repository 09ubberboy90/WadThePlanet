from django import forms
from django.forms import ModelForm
from planet.models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(forms.ModelForm):
    password_copy = forms.CharField(
            label='Confirm password', min_length= 6, max_length= 128,widget = forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class="input_field"),
            Field('password', css_class="input_field"),
            Field('email', css_class="input_field"),
            Field('password_copy', css_class="input_field"),
            Field('avatar'),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )
        self.helper['password'].update_attributes(min_length= 6)

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
        fields = ['email', 'avatar', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput,
        }

