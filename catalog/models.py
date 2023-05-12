from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


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


class Worker(AbstractUser):
    position = models.ForeignKey(
        to=Position,
        on_delete=models.DO_NOTHING,
        null=True
    )
    username = models.CharField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Worker"
        verbose_name_plural = "Workers"
        ordering = ["position"]

    def get_absolute_url(self):
        return reverse("catalog:profile_url_detail", args=[str(self.id)])


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
    assignees = models.ManyToManyField(to=Worker, related_name="assignees")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Tasks"
        ordering = ["-deadline"]
