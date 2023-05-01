from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import generic

from .forms import (
    LoginForm,
)
from .models import (
    Worker,
    Task,
    TaskType,
    Position,
)


# @login_required
def index(request):
    num_task = Task.objects.count()
    num_task_solved = Task.objects.filter(is_completed=True).count()
    num_task_actual = Task.objects.filter(is_completed=False).count()
    num_worker = Worker.objects.count()
    num_position = Position.objects.count()
    num_task_type = TaskType.objects.count()

    # num_visits = request.session.get ("num_visits", 0)
    # request.session["num_visits"] = num_visits
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
    success_url = '/'
    template_name = 'accounts/login.html'

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
