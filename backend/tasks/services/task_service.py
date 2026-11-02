from django.db import transaction
from django.utils import timezone

from tasks.exceptions import DomainError
from tasks.models import Task

MAX_RECURRENCE_INTERVAL = 365


class TaskService:
    """
    Nơi duy nhất chứa quy tắc nghiệp vụ ghi dữ liệu của Task.
    Mọi phụ thuộc (policy, registry, đồng hồ, hook) được tiêm qua constructor
    để dễ thay thế và dễ test.
    """

    def __init__(self, *, transitions, recurrence, bulk_actions, clock,
                 on_completed=(), on_reopened=()):
        self.transitions = transitions
        self.recurrence = recurrence
        self.bulk_actions = bulk_actions
        self._clock = clock
        self._on_completed = list(on_completed)
        self._on_reopened = list(on_reopened)

    # ---- tạo / sửa -------------------------------------------------------

    @transaction.atomic
    def create(self, owner, data):
        data = dict(data)
        tags = data.pop('tags', [])
        if data.get('status', Task.PENDING) == Task.COMPLETED:
            raise DomainError('A new task cannot be created as completed.', field='status')
        self._validate(owner, data, instance=None)
        task = Task(owner=owner, **data)
        task.save()
        task.tags.set(tags)
        return task

    @transaction.atomic
    def update(self, task, data):
        data = dict(data)
        tags = data.pop('tags', None)
        new_status = data.pop('status', None)
        self._validate(task.owner, data, instance=task)
        for field, value in data.items():
            setattr(task, field, value)
        task.save()
        if tags is not None:
            task.tags.set(tags)
        if new_status is not None and new_status != task.status:
            self.change_status(task, new_status)
        return task

    # ---- trạng thái ------------------------------------------------------

    @transaction.atomic
    def change_status(self, task, target):
        previous = task.status
        if target not in dict(Task.STATUS_CHOICES):
            raise DomainError('Invalid status.', field='status')
        if previous == target:
            return task
        self.transitions.ensure(previous, target)
        task.status = target
        task.save()
        if target == Task.COMPLETED:
            self._run(self._on_completed, task)
        elif previous == Task.COMPLETED:
            self._run(self._on_reopened, task)
        return task

    # ---- lưu trữ ---------------------------------------------------------

    @transaction.atomic
    def archive(self, task):
        now = timezone.now()
        Task.objects.filter(pk=task.pk).update(
            archived_at=now, archived_by_parent=False, updated_at=now
        )
        task.subtasks.filter(archived_at__isnull=True).update(
            archived_at=now, archived_by_parent=True, updated_at=now
        )
        task.refresh_from_db()
        return task

    @transaction.atomic
    def restore(self, task):
        now = timezone.now()
        archived_at = task.archived_at
        Task.objects.filter(pk=task.pk).update(
            archived_at=None, archived_by_parent=False, updated_at=now
        )
        if archived_at is not None:
            task.subtasks.filter(archived_by_parent=True).update(
                archived_at=None, archived_by_parent=False, updated_at=now
            )
        task.refresh_from_db()
        return task

    # ---- hàng loạt -------------------------------------------------------

    @transaction.atomic
    def bulk(self, owner, ids, action_name, params=None):
        action = self.bulk_actions.get(action_name)
        context = action.prepare(self, owner, params or {})
        tasks = Task.objects.filter(owner=owner, pk__in=ids)
        affected = 0
        for task in tasks:
            if action.apply(self, task, context):
                affected += 1
        return {'requested': len(set(ids)), 'affected': affected}

    # ---- nội bộ ----------------------------------------------------------

    @staticmethod
    def _run(handlers, task):
        for handler in handlers:
            handler(task)

    def _validate(self, owner, data, instance):
        def effective(field, default=None):
            if field in data:
                return data[field]
            return getattr(instance, field, default) if instance else default

        today = self._clock()

        due_date = effective('due_date')
        if 'due_date' in data and due_date is not None:
            unchanged = instance is not None and instance.due_date == due_date
            if due_date < today and not unchanged:
                raise DomainError('Due date cannot be in the past.', field='due_date')

        parent = effective('parent')
        if parent is not None:
            if parent.owner_id != owner.id:
                raise DomainError('Parent task not found.', field='parent')
            if instance is not None and parent.pk == instance.pk:
                raise DomainError('A task cannot be its own parent.', field='parent')
            if parent.parent_id is not None:
                raise DomainError('Subtasks cannot be nested more than one level.', field='parent')
            if instance is not None and instance.subtasks.exists():
                raise DomainError('A task that has subtasks cannot become a subtask.', field='parent')

        frequency = effective('recurrence_frequency', '')
        if frequency:
            if self.recurrence.get(frequency) is None:
                raise DomainError(
                    f'Unsupported recurrence. Use one of: {", ".join(self.recurrence.keys())}.',
                    field='recurrence_frequency',
                )
            if effective('due_date') is None:
                raise DomainError('A recurring task needs a due date.', field='recurrence_frequency')
            if parent is not None:
                raise DomainError('Subtasks cannot recur.', field='recurrence_frequency')
            interval = effective('recurrence_interval', 1)
            if not 1 <= interval <= MAX_RECURRENCE_INTERVAL:
                raise DomainError(
                    f'Interval must be between 1 and {MAX_RECURRENCE_INTERVAL}.',
                    field='recurrence_interval',
                )
            until = effective('recurrence_until')
            if until is not None and until < effective('due_date'):
                raise DomainError('Recurrence end must not be before the due date.',
                                  field='recurrence_until')
