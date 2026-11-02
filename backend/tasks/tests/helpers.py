from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from tasks.models import Task
from tasks.services import build_task_service

User = get_user_model()


def make_user(name='alice'):
    return User.objects.create_user(name, f'{name}@example.com', 'S3cure-pass-123')


def today():
    return timezone.localdate()


def days_from_today(n):
    return today() + timedelta(days=n)


def make_task(owner, **kwargs):
    kwargs.setdefault('title', 'task')
    return Task.objects.create(owner=owner, **kwargs)


def service_at(fixed_day: date):
    """TaskService với đồng hồ cố định để test không phụ thuộc ngày chạy."""
    return build_task_service(clock=lambda: fixed_day)
