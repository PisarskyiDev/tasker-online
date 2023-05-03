from django.contrib.auth.views import LogoutView
from django.urls import path

from catalog.views import (
    index,
    LoginView,
    SignUpView,
    TaskListView,
    TaskDetailView,
    update_task_status,
)

urlpatterns = [
    path("", index, name="index"),
    path("login/", LoginView.as_view(), name="login"),
    path("task/", TaskListView.as_view(), name="task_url_list"),
    path('task/<int:pk>/update_status/', update_task_status, name='update_task_status'),
    path("task/<int:pk>/", TaskDetailView.as_view(), name="task_url_detail"),
    path("registrate/", SignUpView.as_view(), name="registrate"),
    path('logout/', LogoutView.as_view(next_page='catalog:index'), name='logout')
]

app_name = 'catalog'
