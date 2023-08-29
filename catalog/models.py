from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


def get_worker_model():
    from user.models import Worker

    return Worker


class TaskType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=155, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(models.Model):
    STR_CHOICES = [
        ("!!!", "Extra priority"),
        ("!!", "Priority"),
        ("!", "Standard"),
        ("", "No priority"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    is_completed = models.BooleanField(default=True)
    priority = models.CharField(max_length=3, choices=STR_CHOICES)
    task_type = models.ForeignKey(to=TaskType, on_delete=models.DO_NOTHING)
    assignees = models.ManyToManyField(to=get_worker_model(), related_name="assignees")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Tasks"
        ordering = ["-deadline"]
