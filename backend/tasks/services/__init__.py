"""Composition root của lớp service: lắp các thành phần mặc định lại với nhau."""
from django.utils import timezone

from tasks.domain.recurrence import build_default_registry
from tasks.domain.status import StatusTransitionPolicy
from tasks.services.bulk import build_default_bulk_registry
from tasks.services.handlers import (
    CascadeCompleteSubtasks,
    ReopenCompletedParent,
    SpawnNextOccurrence,
)
from tasks.services.task_service import TaskService


def build_task_service(clock=timezone.localdate):
    recurrence = build_default_registry()
    return TaskService(
        transitions=StatusTransitionPolicy(),
        recurrence=recurrence,
        bulk_actions=build_default_bulk_registry(),
        clock=clock,
        on_completed=[CascadeCompleteSubtasks(), SpawnNextOccurrence(recurrence, clock)],
        on_reopened=[ReopenCompletedParent()],
    )


def get_task_service():
    # Tạo mới mỗi lần để clock mặc định luôn đọc thời gian hiện tại và test dễ thay thế.
    return build_task_service()
