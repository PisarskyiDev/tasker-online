from datetime import date
from social_core.exceptions import AuthMissingParameter
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.http import require_POST
from social_django.models import Code

from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site

import task_manager.settings
from tokens.account_activation_token import token_manager
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string

from .forms import (
    LoginForm,
    RegistrationForm,
    TaskForm,
    ProfileForm,
)
from .models import (
    Task,
    TaskType,
    Position,
)
from user.models import Worker


def index(request):
    num_task = Task.objects.count()
    num_task_solved = Task.objects.filter(is_completed=False).count()
    num_task_actual = Task.objects.filter(is_completed=True).count()
    num_worker = Worker.objects.count()
    num_position = Position.objects.count()
    num_task_type = TaskType.objects.count()

    context = {
        "num_task": num_task,
        "num_worker": num_worker,
        "num_position": num_position,
        "num_task_type": num_task_type,
        "num_task_solved": num_task_solved,
        "num_task_actual": num_task_actual,
    }
    return render(request, "catalog/index.html", context=context)


class LoginView(generic.FormView):
    form_class = LoginForm
    template_name = "accounts/login.html"

    def get_success_url(self):
        return self.request.GET.get("next") or reverse_lazy("catalog:index")

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


def signup(request):
    user_model = get_user_model()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        form_valid = True if form.is_valid() else False
        if form_valid:
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = "Activate your account."
            message = render_to_string(
                "email_template.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": token_manager.make_token(user),
                },
            )
            to_email = form.cleaned_data.get("email")
            sender = task_manager.settings.EMAIL_HOST_USER
            send_mail(mail_subject, message, sender, [to_email])
            return HttpResponse(
                "Please confirm your email address to complete the registration"
            )
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and token_manager.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse(
            "Thank you for your email confirmation. Now you can login your account."
        )
    else:
        return HttpResponse("Activation link is invalid!")


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "catalog/task_list.html"
    context_object_name = "tasks_view_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        context["num_task_actual"] = Task.objects.filter(is_completed=True).count()

        context["today"] = date.today()
        deadline = None

        for task in context["tasks_view_list"]:
            prefix = "days"
            deadline_date = (task.deadline - today).days
            if deadline_date == 1:
                prefix = "day"
            deadline = f"{deadline_date} {prefix} left"
            if not deadline_date:
                deadline = "Today is deadline"
            task.days_left = deadline

        return context


@method_decorator(require_POST, name="dispatch")
class TaskStatusUpdateView(generic.View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.is_completed = not task.is_completed
        task.save()
        return JsonResponse({"is_completed": task.is_completed})


class TaskDetailView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "catalog/task_detail.html"
    success_url = reverse_lazy("catalog:task_url_list")


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "catalog/task_create.html"
    success_url = reverse_lazy("catalog:task_url_list")


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy("catalog:task_url_list")


class ProfileView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    form_class = ProfileForm
    template_name = "catalog/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        task = Task.objects.filter(assignees=self.request.user)
        actual_task = task.filter(is_completed=True).count()
        solved_task = task.filter(is_completed=False).count()
        context["today"] = today
        context["actual_task"] = actual_task
        context["solved_task"] = solved_task
        return context

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(request=self.request, **self.get_form_kwargs())

    def form_valid(self, form):
        current_user = self.request.user
        if form.instance.pk != current_user.pk and not current_user.is_superuser:
            return HttpResponseForbidden("You are not allowed to edit this profile.")
        return super().form_valid(form)


def page_not_found(request, exception):
    return render(request, "http_response/page-404.html", status=404)


def permission_denied(request, exception):
    return render(request, "http_response/page-403.html", status=403)


def server_error(request):
    try:
        if "google-oauth2" in request.backend.name:
            with transaction.atomic():
                old_code = request.GET.get("verification_code")
                user = Code.objects.get(code=old_code, verified=False)
                email = user.email
                worker = Worker.objects.get(email=email)
                worker.waiting_verified = False
                worker.save()
                user.delete()
            return render(request, "http_response/google-500.html", status=500)
    except (AuthMissingParameter, AttributeError, Code.DoesNotExist) as e:
        return render(request, "http_response/page-500.html", status=500)
