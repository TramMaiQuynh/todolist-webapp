from tasks.exceptions import InvalidTransition
from tasks.models import Task

# Bảng chuyển trạng thái hợp lệ. Muốn thêm trạng thái mới chỉ cần thêm dữ liệu
# vào bảng (hoặc truyền bảng khác vào StatusTransitionPolicy), không sửa logic.
DEFAULT_TRANSITIONS = {
    Task.PENDING: {Task.IN_PROGRESS, Task.COMPLETED},
    Task.IN_PROGRESS: {Task.PENDING, Task.COMPLETED},
    Task.COMPLETED: {Task.PENDING, Task.IN_PROGRESS},  # mở lại
}


class StatusTransitionPolicy:
    def __init__(self, transitions=None):
        self._transitions = transitions or DEFAULT_TRANSITIONS

    def can_transition(self, current, target):
        return target in self._transitions.get(current, set())

    def ensure(self, current, target):
        if not self.can_transition(current, target):
            raise InvalidTransition(current, target)
