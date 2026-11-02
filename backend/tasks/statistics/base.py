from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

from django.db.models import QuerySet


@dataclass(frozen=True)
class StatsContext:
    """Dữ liệu đầu vào chung cho mọi metric."""
    all_tasks: QuerySet      # kể cả task đã lưu trữ (dùng cho lịch sử hoàn thành)
    active_tasks: QuerySet   # chưa lưu trữ (dùng cho số liệu hiện tại)
    today: date
    days: int                # độ dài cửa sổ xu hướng


class Metric(ABC):
    """Strategy: mỗi metric tự tính một khối số liệu."""
    key = ''

    @abstractmethod
    def compute(self, ctx: StatsContext) -> dict:
        ...


class MetricRegistry:
    """Thêm metric mới = register() một class mới, không sửa registry hay view."""

    def __init__(self, metrics=()):
        self._metrics = {}
        for metric in metrics:
            self.register(metric)

    def register(self, metric: Metric):
        self._metrics[metric.key] = metric

    def compute_all(self, ctx: StatsContext) -> dict:
        return {key: metric.compute(ctx) for key, metric in self._metrics.items()}
