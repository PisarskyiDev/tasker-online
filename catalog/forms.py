from datetime import date

from django.contrib.auth import forms as auth, authenticate
from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateInput

from .models import Task
from user.models import Worker


class LoginForm(auth.AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        wait_verification = Worker.objects.filter(
            email=username, is_active=False, waiting_verified=True
        )
        try:
            passwords_match = wait_verification.get().check_password(password)
        except Worker.DoesNotExist:
            passwords_match = False
        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if wait_verification and passwords_match:
                raise ValidationError(
                    "This account is inactive. Check your email and activate your account.",
                    code="inactive",
                )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    class Meta:
        model = Worker


class RegistrationForm(auth.UserCreationForm):
    username = forms.CharField(label="Username", required=False)
    first_name = forms.CharField(label="First name", required=False)
    email = forms.EmailField(label="Email", required=True)

    class Meta(auth.UserCreationForm.Meta):
        model = Worker
        fields = auth.UserCreationForm.Meta.fields + (
            "username",
            "email",
            "first_name",
            "last_name",
            "position",
        )
        widgets = {
            "position": forms.RadioSelect(),
        }

    def save(self, commit=True):
        worker = super().save(commit=False)
        if commit:
            worker.save()
            self.save_m2m()
        return worker


class TaskForm(forms.ModelForm):
    deadline = forms.DateField(widget=DateInput(attrs={"type": "date"}))

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
        widgets = {
            "assignees": forms.CheckboxSelectMultiple(),
            "priority": forms.RadioSelect(),
            "task_type": forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["priority"].required = False

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if deadline and deadline < date.today():
            raise forms.ValidationError("The date cannot be in the past.")
        return deadline


class ProfileForm(forms.ModelForm):
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_user = request.user
        # <-- if current_user.is_superuser then he can edit eny profile -->
        if current_user.is_superuser:
            self.fields["username"].required = True
        # <-- if current_user.is_superuser he can edit only own profile-->
        if not current_user.is_superuser and self.instance.pk != current_user.id:
            self.fields["username"].disabled = True
            self.fields["first_name"].disabled = True
            self.fields["last_name"].disabled = True
            self.fields["email"].disabled = True
            self.fields["date_joined"].disabled = True
            self.fields["position"].disabled = True

    class Meta:
        model = Worker
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "position",
        ]
        widgets = {
            "position": forms.RadioSelect(),
        }
