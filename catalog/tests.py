from django.test import TestCase
from django.contrib.auth import forms as auth
from unittest.mock import patch
from .models import Task, TaskType, Worker, Position
from .forms import LoginForm, RegistrationForm
from django.test import RequestFactory
from django.urls import reverse


class LoginFormTestCase(TestCase):
    def test_login_form_meta_model(self):
        self.assertEqual(LoginForm.Meta.model, Worker)


class RegistrationFormTestCase(TestCase):
    def test_registration_form_meta_model(self):
        self.assertEqual(RegistrationForm.Meta.model, Worker)

    def test_registration_form_meta_fields(self):
        expected_fields = auth.UserCreationForm.Meta.fields + (
            "username",
            "email",
            "first_name",
            "last_name",
            "position",
        )
        self.assertEqual(RegistrationForm.Meta.fields, expected_fields)


class TaskModelTestCase(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="Test Task Type")
        self.worker = Worker.objects.create(username="testuser")
        self.position = Position.objects.create(name="Test Position")
        self.task = Task.objects.create(
            name="Test Task",
            description="Test description",
            deadline="2023-01-01",
            is_completed=True,
            priority="!",
            task_type=self.task_type
        )
        self.task.assignees.set([self.worker])

    def test_task_str_representation(self):
        self.assertEqual(str(self.task), "Test Task")

    def test_task_priority_choices(self):
        priority_choices = [choice[0] for choice in Task.STR_CHOICES]
        self.assertIn(self.task.priority, priority_choices)

    def test_task_task_type_foreign_key(self):
        self.assertEqual(self.task.task_type, self.task_type)

    def test_task_assignees_many_to_many(self):
        self.assertEqual(self.task.assignees.count(), 1)
        self.assertEqual(self.task.assignees.first(), self.worker)


class WorkerModelTestCase(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Test Position")
        self.worker = Worker.objects.create(
            username="testuser",
            position=self.position
        )

    def test_worker_str_representation(self):
        self.assertEqual(str(self.worker), "testuser")

    def test_worker_meta_verbose_names(self):
        self.assertEqual(Worker._meta.verbose_name, "Worker")
        self.assertEqual(Worker._meta.verbose_name_plural, "Workers")

    def test_worker_meta_ordering(self):
        self.assertEqual(Worker._meta.ordering, ["position"])

    @patch("catalog.models.reverse")
    def test_worker_get_absolute_url(self, mock_reverse):
        mock_reverse.return_value = "/catalog/profile/1/"
        url = self.worker.get_absolute_url()
        mock_reverse.assert_called_once_with(
            "catalog:profile_url_detail", args=["1"]
        )
        self.assertEqual(url, "/catalog/profile/1/")


class URLTestCase(TestCase):
    def test_index_url(self):
        url = reverse('catalog:index')
        self.assertEqual(url, '/')

    def test_signup_url(self):
        url = reverse('catalog:registrate')
        self.assertEqual(url, '/registrate/')

    def test_login_url(self):
        url = reverse('catalog:login')
        self.assertEqual(url, '/login/')

    def test_logout_url(self):
        url = reverse('catalog:logout')
        self.assertEqual(url, '/logout/')

    def test_task_list_url(self):
        url = reverse('catalog:task_url_list')
        self.assertEqual(url, '/task/')

    def test_task_create_url(self):
        url = reverse('catalog:task_url_create')
        self.assertEqual(url, '/task/create/')

    def test_task_status_update_url(self):
        task_id = 1  # Provide an existing task ID here
        url = reverse('catalog:update_task_status', args=[task_id])
        self.assertEqual(url, f'/task/{task_id}/update_status/')

    def test_task_detail_url(self):
        task_id = 1  # Provide an existing task ID here
        url = reverse('catalog:task_url_detail', args=[task_id])
        self.assertEqual(url, f'/task/{task_id}/')


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Worker.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_login_view_get(self):
        response = self.client.get(reverse("catalog:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_view_post_valid_credentials(self):
        url = reverse("catalog:login")
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse("catalog:index"))

    def test_login_view_post_invalid_credentials(self):
        url = reverse("catalog:login")
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")


class SignUpViewTestCase(TestCase):
    def test_signup_view_get(self):
        response = self.client.get(reverse("catalog:registrate"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_signup_view_post_invalid_data(self):
        url = reverse("catalog:registrate")
        data = {
            "username": "testuser",
            "password1": "testpassword",
            "password2": "differentpassword",
            "email": "invalid_email",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")
