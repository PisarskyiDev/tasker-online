from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div
from crispy_forms.layout import Submit
from django.contrib.auth import forms as auth
from django import forms
from django.forms import DateInput

from .models import Worker, Position, Task


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


class TaskBaseForm(forms.ModelForm):
    deadline = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    assignees = forms.ModelMultipleChoiceField(
        queryset=Worker.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-label'})
    )

    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "deadline",
            "priority",
            "task_type",
            "assignees",
        ]


class TaskCreateForm(TaskBaseForm):
    pass


class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "priority",
            "task_type",
            "assignees",
        ]
        widgets = {
            "assignees": forms.CheckboxSelectMultiple(),
            "task_type": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
        # Add crispy classes to priority field
        self.fields['priority'].widget.attrs.update({'class': 'form-select'})