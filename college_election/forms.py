from django import forms
from django.core.exceptions import ValidationError

from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, DateInput, DateTimeInput


class LoginForm(forms.Form):
    user_id = forms.CharField(required=True, min_length=3, max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


#
# class RegisterEmployeeForm(UserCreationForm):
#     class Meta(UserCreationForm.Meta):
#         model = Account
#         fields = ['user_id', ]
#
#     def __init__(self, *args, **kwargs):
#         super(RegisterEmployeeForm, self).__init__(*args, **kwargs)
#         for visible in self.visible_fields():
#             visible.field.widget.attrs['class'] = 'form-control'


class ElectionInfoForm(ModelForm):
    class Meta:
        model = Election
        fields = ['title', 'voting_start', 'voting_end']
        widgets = {
            'voting_start': DateInput(attrs={'type': 'date'}),
            'voting_end': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(ElectionInfoForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
