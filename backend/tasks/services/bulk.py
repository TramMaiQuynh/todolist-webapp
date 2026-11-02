"""
Thao tác hàng loạt. Mỗi hành động là một Strategy đăng ký theo tên; thêm hành động
mới chỉ cần viết class mới và register(), không sửa BulkActionRegistry hay view.
"""
from abc import ABC, abstractmethod

from tasks.exceptions import DomainError
from tasks.models import Category, Task


class BulkAction(ABC):
    name = ''

    def prepare(self, service, owner, params):
        """Kiểm tra/đọc tham số một lần cho cả lô. Trả về dữ liệu dùng lại cho apply."""
        return None

    @abstractmethod
    def apply(self, service, task, context) -> bool:
        """Trả True nếu đã áp dụng, False nếu bỏ qua task này."""


class CompleteAction(BulkAction):
    name = 'complete'

    def apply(self, service, task, context):
        if not service.transitions.can_transition(task.status, Task.COMPLETED):
            return False
        service.change_status(task, Task.COMPLETED)
        return True


class ReopenAction(BulkAction):
    name = 'reopen'

    def apply(self, service, task, context):
        if task.status != Task.COMPLETED:
            return False
        service.change_status(task, Task.PENDING)
        return True


class ArchiveAction(BulkAction):
    name = 'archive'

    def apply(self, service, task, context):
        if task.is_archived:
            return False
        service.archive(task)
        return True


class RestoreAction(BulkAction):
    name = 'restore'

    def apply(self, service, task, context):
        if not task.is_archived:
            return False
        service.restore(task)
        return True


class DeleteAction(BulkAction):
    name = 'delete'

    def apply(self, service, task, context):
        task.delete()
        return True


class SetPriorityAction(BulkAction):
    name = 'set_priority'

    def prepare(self, service, owner, params):
        priority = params.get('priority')
        if priority not in dict(Task.PRIORITY_CHOICES):
            raise DomainError('Invalid priority.', field='priority')
        return priority

    def apply(self, service, task, context):
        if task.priority == context:
            return False
        task.priority = context
        task.save()
        return True


class SetCategoryAction(BulkAction):
    name = 'set_category'

    def prepare(self, service, owner, params):
        category_id = params.get('category')
        if category_id in (None, ''):
            return None
        from django.db.models import Q
        category = Category.objects.filter(
            Q(owner=owner) | Q(owner__isnull=True), pk=category_id
        ).first()
        if category is None:
            raise DomainError('Category not found.', field='category')
        return category

    def apply(self, service, task, context):
        if task.category_id == (context.pk if context else None):
            return False
        task.category = context
        task.save()
        return True


class BulkActionRegistry:
    def __init__(self, actions=()):
        self._actions = {}
        for action in actions:
            self.register(action)

    def register(self, action: BulkAction):
        self._actions[action.name] = action

    def get(self, name):
        action = self._actions.get(name)
        if action is None:
            raise DomainError(f'Unknown bulk action "{name}".', field='action')
        return action

    def names(self):
        return list(self._actions)


def build_default_bulk_registry():
    return BulkActionRegistry([
        CompleteAction(), ReopenAction(), ArchiveAction(), RestoreAction(),
        DeleteAction(), SetPriorityAction(), SetCategoryAction(),
    ])
