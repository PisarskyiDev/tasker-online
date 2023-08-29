from django.contrib import admin
from django.contrib.auth.models import Group

from .models import (
    Task,
    Position,
    TaskType,
)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    pass


@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    pass


admin.site.unregister(Group)
