from datetime import date

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.http import require_POST

from .forms import (
    LoginForm,
    RegistrationForm,
    TaskCreateForm,
    TaskUpdateForm,
)
from .models import (
    Worker,
    Task,
    TaskType,
    Position,
)


def index(request):
    num_task = Task.objects.count()
    num_task_solved = Task.objects.filter(is_completed=True).count()
    num_task_actual = Task.objects.filter(is_completed=False).count()
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
    return render(request, "home/index.html", context=context)


class LoginView(generic.FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        return self.request.GET.get('next')

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
        for task in context['tasks_view_list']:
            days_left = (task.deadline - today).days
            if days_left == 1:
                task.days_left = str(days_left) + " " + "day left"
            if days_left == 0:
                task.days_left = "Today is deadline"
            else:
                task.days_left = str(days_left) + " " + "days left"
        return context


@require_POST
def update_task_status(request, pk):
    # кнопка done/open на представлении экземпляра в шаблоне task_list.html

    task = get_object_or_404(Task, pk=pk)
    task.is_completed = not task.is_completed
    task.save()
    return JsonResponse({'is_completed': task.is_completed})


# class TaskDetailView(LoginRequiredMixin, generic.DetailView):
#     model = Task
#     template_name = 'catalog/task_detail.html'


class TaskDetailView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskUpdateForm
    template_name = 'catalog/task_detail.html'
    success_url = reverse_lazy('catalog:task_url_list')


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "catalog/task_form.html"
    fields = [
        "name",
        "description",
        "deadline",
        "is_completed",
        "priority",
        "task_type",
        "assignees",
    ]


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskUpdateForm
    template_name = "catalog/task_form.html"
    fields = [
        "name",
        "description",
        "deadline",
        "is_completed",
        "priority",
        "task_type",
        "assignees",
    ]


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    template_name = "catalog/task_confirm_delete.html"
    success_url = reverse_lazy("tasks")

