from tasks.statistics.base import MetricRegistry, StatsContext
from tasks.statistics.metrics import (
    BreakdownMetric,
    DeadlinesMetric,
    OverviewMetric,
    PerformanceMetric,
    TrendMetric,
    WorkloadMetric,
)


def build_default_metric_registry():
    return MetricRegistry([
        OverviewMetric(), DeadlinesMetric(), BreakdownMetric(), TrendMetric(),
        PerformanceMetric(), WorkloadMetric(),
    ])


__all__ = ['StatsContext', 'MetricRegistry', 'build_default_metric_registry']
