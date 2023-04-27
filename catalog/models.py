from django.contrib.auth.models import AbstractUser
from django.db import models


class TaskType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=155)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(to=Position, on_delete=models.DO_NOTHING)
    username = models.CharField(max_length=100, unique=True, blank=True)
    first_name = models.CharField(max_length=100)
    las_name = models.CharField(max_length=100)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Worker"
        verbose_name_plural = "Workers"
        ordering = ["position"]


class Task(models.Model):
    STR_CHOICES = [
        ("!!!", "Urgent"),
        ("!!", "Usually"),
        ("!", "Deliberately"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=3, choices=STR_CHOICES)
    task_type = models.ForeignKey(to=TaskType, on_delete=models.DO_NOTHING)
    assignees = models.ManyToManyField(to=Worker)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Tasks"
        ordering = ["-deadline"]
