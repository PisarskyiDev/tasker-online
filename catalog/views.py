from datetime import date

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.http import require_POST

from .forms import (
    LoginForm,
    RegistrationForm,
    TaskForm,
    ProfileForm,
)
from .models import (
    Worker,
    Task,
    TaskType,
    Position,
)


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
    template_name = 'accounts/login.html'

    def get_success_url(self):
        return self.request.GET.get('next') or reverse_lazy('catalog:index')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
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


class SignUpView(generic.CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('catalog:login')
    template_name = 'accounts/register.html'


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = 'catalog/task_list.html'
    context_object_name = 'tasks_view_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        context['num_task_actual'] = Task.objects.filter(is_completed=True).count()
        context['today'] = date.today()
        assignees = []
        for task in context['tasks_view_list']:
            days_left = (task.deadline - today).days
            if days_left == 1:
                task.days_left = str(days_left) + " " + "day left"
            if days_left == 0:
                task.days_left = "Today is deadline"
            else:
                task.days_left = str(days_left) + " " + "days left"
            assignees.extend(list(task.assignees.all()))
        context['assignees'] = assignees
        return context


@require_POST
def update_task_status(request, pk):
    # кнопка done/open на представлении экземпляра в шаблоне task_list.html

    task = get_object_or_404(Task, pk=pk)
    task.is_completed = not task.is_completed
    task.save()
    return JsonResponse({'is_completed': task.is_completed})


class TaskDetailView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'catalog/task_detail.html'
    success_url = reverse_lazy('catalog:task_url_list')


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "catalog/task_create.html"
    success_url = reverse_lazy('catalog:task_url_list')


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy('catalog:task_url_list')


class ProfileView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    form_class = ProfileForm
    template_name = 'catalog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        actual_task = Task.objects.filter(assignees=self.request.user, is_completed=True).count()
        solved_task = Task.objects.filter(assignees=self.request.user, is_completed=False).count()
        context['today'] = today
        context['actual_task'] = actual_task
        context['solved_task'] = solved_task
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
    return render(request, 'http_response/page-404.html', status=404)


def permission_denied(request, exception):
    return render(request, 'http_response/page-403.html', status=403)


def server_error(request):
    return render(request, 'http_response/page-500.html', status=500)
