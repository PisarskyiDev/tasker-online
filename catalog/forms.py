from datetime import date

from django.contrib.auth import forms as auth
from django import forms
from django.forms import DateInput
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import Worker, Task


class LoginForm(auth.AuthenticationForm):
    class Meta:
        model = Worker


class RegistrationForm(auth.UserCreationForm):
    username = forms.CharField(label="Username", required=True)
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
            self.fields["date_joined"].disabled = True
            self.fields["date_joined"].required = False
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
            "date_joined",
            "position",
        ]
        widgets = {
            "position": forms.RadioSelect(),
        }


class PasswordForm(forms.Form):
    secret_word = forms.CharField(max_length=10)


def collect_password(strategy, backend, request, details, *args, **kwargs):
    if request.method == "POST":
        form = PasswordForm(request.POST)
        if form.is_valid():
            # Сохраняем введенный пароль в сессии для передачи в пайплайн
            request.session["local_password"] = form.cleaned_data["secret_word"]

            # Перенаправляем на завершение пайплайна
            return redirect(reverse("social:complete", args=("google-oauth2",)))
    else:
        form = PasswordForm()

    return render(request, "password_form.html", {"form": form})
