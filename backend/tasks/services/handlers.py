"""
Các hook chạy khi một task đổi trạng thái (Observer).
Thêm hành vi mới = viết thêm một callable và truyền vào TaskService, không sửa code cũ.
"""
from tasks.models import Task

MAX_SKIPPED_OCCURRENCES = 10_000


class CascadeCompleteSubtasks:
    """Hoàn thành task cha thì mọi task con chưa xong cũng được hoàn thành."""

    def __call__(self, task):
        for child in task.subtasks.exclude(status=Task.COMPLETED):
            child.status = Task.COMPLETED
            child.save()


class SpawnNextOccurrence:
    """Task lặp được hoàn thành -> tạo lần xuất hiện kế tiếp."""

    def __init__(self, registry, clock):
        self._registry = registry
        self._clock = clock

    def __call__(self, task):
        rule = self._registry.get(task.recurrence_frequency)
        if rule is None or task.due_date is None or task.parent_id is not None:
            return None

        today = self._clock()
        next_due = rule.next_date(task.due_date, task.recurrence_interval)
        # Bỏ qua các kỳ đã trôi qua nếu hoàn thành trễ
        for _ in range(MAX_SKIPPED_OCCURRENCES):
            if next_due >= today:
                break
            next_due = rule.next_date(next_due, task.recurrence_interval)

        if task.recurrence_until and next_due > task.recurrence_until:
            return None

        clone = Task.objects.create(
            owner=task.owner,
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=next_due,
            estimated_minutes=task.estimated_minutes,
            category=task.category,
            is_important=task.is_important,
            recurrence_frequency=task.recurrence_frequency,
            recurrence_interval=task.recurrence_interval,
            recurrence_until=task.recurrence_until,
        )
        clone.tags.set(task.tags.all())
        return clone


class ReopenCompletedParent:
    """Mở lại một task con thì task cha đã hoàn thành phải quay về 'đang làm'."""

    def __call__(self, task):
        parent = task.parent
        if parent is not None and parent.status == Task.COMPLETED:
            parent.status = Task.IN_PROGRESS
            parent.save()
