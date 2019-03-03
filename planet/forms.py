from django import forms
from django.forms import ModelForm
from planet.models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import FormActions
from django.core.exceptions import ValidationError

class RegistrationForm(forms.ModelForm):
    username = forms.CharField(
        label='Username', min_length=6, max_length=32, help_text=('Required. 32 characters or fewer. Letters and digits only.'))
    password_copy = forms.CharField(
            label='Confirm password', min_length= 6, max_length= 128,widget = forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class="input_field"),
            Field('email', css_class="input_field"),
            Field('password', css_class="input_field"),
            Field('password_copy', css_class="input_field"),
            Field('avatar'),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )
        self.helper['password'].update_attributes(min_length= 6)

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
            email=self.cleaned_data['email'],
            password = self.cleaned_data['password'],
            avatar = self.cleaned_data['avatar']
        )
        return user

    class Meta:
        model = PlanetUser
        fields = ['email', 'avatar', 'password']
        widgets = {
            'password': forms.PasswordInput,
        }

class LoggingForm(forms.Form):
    username = forms.CharField(
        label='Username', min_length=6, max_length=32)

    password = forms.CharField(
        label='Password', min_length=6, max_length=128, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )

        )

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return password
class AvatarForm(forms.Form):
    avatar = models.ImageField(
        upload_to=content_file_name, blank=True, null=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )

        )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment', 'rating']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Field('comment', id='comment',
                    wrapper_class='col-8'),
                Field('rating', id='rating',
                    wrapper_class='col-2'),
                ButtonHolder(
                    Submit('send', 'Send', id='send', css_class='btn-sm'),
                    css_class='send-btn-container col-2 pb-3 align-self-end',
                ),
            )
        )
