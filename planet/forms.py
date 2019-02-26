from django import forms
from django.forms import ModelForm
from planet.models import *


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

        def __init__(self, *args, **kwargs):
            super(UserForm, self).__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.form_id = 'UserForm'
            self.helper.form_class = 'userclass'
            self.helper.form_method = 'post'
            self.helper.form_action = 'submit_survey'
            self.helper.add_input(Submit('submit', 'Submit'))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['picture']
        def __init__(self, *args, **kwargs):
            super(UserForm, self).__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.form_id = 'UserForm'
            self.helper.form_class = 'userclass'
            self.helper.form_method = 'post'
            self.helper.form_action = 'submit_survey'
            self.helper.add_input(Submit('submit', 'Submit'))
