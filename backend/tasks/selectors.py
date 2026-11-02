"""Các truy vấn đọc dữ liệu, luôn giới hạn theo user để không lộ dữ liệu chéo."""
from django.db.models import Case, Count, IntegerField, Q, Value, When

from tasks.models import Category, Tag, Task


def tasks_for(user):
    return (
        Task.objects.filter(owner=user)
        .select_related('category', 'parent')
        .prefetch_related('tags')
        .annotate(
            subtask_count=Count('subtasks', distinct=True),
            subtasks_done=Count(
                'subtasks', filter=Q(subtasks__status=Task.COMPLETED), distinct=True
            ),
            priority_rank=Case(
                When(priority='Low', then=Value(1)),
                When(priority='Medium', then=Value(2)),
                When(priority='High', then=Value(3)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
        .order_by('-created_at', '-id')  # annotate(Count) làm mất Meta.ordering
    )


def categories_for(user):
    """Danh mục mặc định + danh mục của user; task_count chỉ đếm task của user."""
    return (
        Category.objects.filter(Q(owner=user) | Q(owner__isnull=True))
        .annotate(task_count=Count('tasks', filter=Q(tasks__owner=user), distinct=True))
        .order_by('name', 'id')
    )


def tags_for(user):
    return (
        Tag.objects.filter(owner=user)
        .annotate(task_count=Count('tasks', distinct=True))
        .order_by('name', 'id')
    )
