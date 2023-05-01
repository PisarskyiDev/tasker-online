from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import generic

from catalog.models import Worker, Task, TaskType, Position


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


class WorkersListView(generic.ListView):
    template_name = "home/workers"

