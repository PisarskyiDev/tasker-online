from django.contrib.auth import forms as auth
from django import forms
from django.forms import CheckboxSelectMultiple

from .models import Worker, Position


class LoginForm(auth.AuthenticationForm):
    class Meta:
        model = Worker


class RegistrationForm(auth.UserCreationForm):
    username = forms.CharField(label='Username', required=True)
    first_name = forms.CharField(label='First name', required=False)
    email = forms.EmailField(label='Email', required=True)
    position = forms.ModelMultipleChoiceField(
        queryset=Position.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-label'})
    )

    class Meta(auth.UserCreationForm.Meta):
        model = Worker
        fields = auth.UserCreationForm.Meta.fields + (
            'username',
            'email',
            'first_name',
            'last_name',
            'position',
        )

    def save(self, commit=True):
        worker = super().save(commit=False)
        if commit:
            worker.save()
            self.save_m2m()
        return worker

    def clean_position(self):
        return self.cleaned_data['position'].get()
