from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from tasks.models import Task
from tasks.statistics.base import Metric, StatsContext


def _open(qs):
    return qs.exclude(status=Task.COMPLETED)


class OverviewMetric(Metric):
    key = 'overview'

    def compute(self, ctx: StatsContext):
        qs = ctx.active_tasks
        by_status = {s: 0 for s, _ in Task.STATUS_CHOICES}
        for row in qs.values('status').annotate(n=Count('id')):
            by_status[row['status']] = row['n']
        total = sum(by_status.values())
        completed = by_status[Task.COMPLETED]
        return {
            'total': total,
            'open': total - completed,
            'by_status': by_status,
            'completion_rate': round(completed / total * 100, 1) if total else 0.0,
        }


class DeadlinesMetric(Metric):
    key = 'deadlines'

    def compute(self, ctx: StatsContext):
        open_tasks = _open(ctx.active_tasks)
        today = ctx.today
        return {
            'overdue': open_tasks.filter(due_date__lt=today).count(),
            'due_today': open_tasks.filter(due_date=today).count(),
            'due_next_7_days': open_tasks.filter(
                due_date__gt=today, due_date__lte=today + timedelta(days=7)
            ).count(),
            'no_due_date': open_tasks.filter(due_date__isnull=True).count(),
        }


class BreakdownMetric(Metric):
    key = 'breakdown'

    def compute(self, ctx: StatsContext):
        open_tasks = _open(ctx.active_tasks)
        by_priority = {p: 0 for p, _ in Task.PRIORITY_CHOICES}
        for row in open_tasks.values('priority').annotate(n=Count('id')):
            by_priority[row['priority']] = row['n']
        by_category = [
            {'category': row['category__name'] or 'Uncategorized', 'count': row['n']}
            for row in open_tasks.values('category__name').annotate(n=Count('id')).order_by('-n')
        ]
        return {'open_by_priority': by_priority, 'open_by_category': by_category}


class TrendMetric(Metric):
    """Số task tạo mới / hoàn thành theo từng ngày trong cửa sổ `days`, đã điền đủ ngày 0."""
    key = 'trend'

    def compute(self, ctx: StatsContext):
        start = ctx.today - timedelta(days=ctx.days - 1)
        completed = dict(
            ctx.all_tasks.filter(completed_at__date__gte=start, completed_at__date__lte=ctx.today)
            .annotate(day=TruncDate('completed_at'))
            .values_list('day').annotate(n=Count('id'))
        )
        created = dict(
            ctx.all_tasks.filter(created_at__date__gte=start, created_at__date__lte=ctx.today)
            .annotate(day=TruncDate('created_at'))
            .values_list('day').annotate(n=Count('id'))
        )
        series = []
        for offset in range(ctx.days):
            day = start + timedelta(days=offset)
            series.append({
                'date': day.isoformat(),
                'created': created.get(day, 0),
                'completed': completed.get(day, 0),
            })
        return {'days': ctx.days, 'series': series}


class PerformanceMetric(Metric):
    key = 'performance'

    def compute(self, ctx: StatsContext):
        start = ctx.today - timedelta(days=ctx.days - 1)
        done = list(
            ctx.all_tasks.filter(
                status=Task.COMPLETED,
                completed_at__date__gte=start,
                completed_at__date__lte=ctx.today,
            )
            .values_list('created_at', 'completed_at', 'due_date')
        )
        with_deadline = [(c, d) for _, c, d in done if d is not None]
        on_time = sum(
            1 for completed_at, due in with_deadline
            if timezone.localtime(completed_at).date() <= due
        )
        hours = [(c - created).total_seconds() / 3600 for created, c, _ in done]
        return {
            'completed_in_window': len(done),
            'on_time_rate': round(on_time / len(with_deadline) * 100, 1) if with_deadline else None,
            'avg_completion_hours': round(sum(hours) / len(hours), 1) if hours else None,
        }


class WorkloadMetric(Metric):
    """Khối lượng việc dự kiến cho 7 ngày tới (số task và số phút ước tính)."""
    key = 'workload'

    def compute(self, ctx: StatsContext):
        open_tasks = _open(ctx.active_tasks)
        horizon = ctx.today + timedelta(days=6)
        rows = {
            row['due_date']: row
            for row in open_tasks.filter(due_date__gte=ctx.today, due_date__lte=horizon)
            .values('due_date')
            .annotate(n=Count('id'), unestimated=Count('id', filter=Q(estimated_minutes__isnull=True)))
        }
        minutes = {}
        for due, est in open_tasks.filter(
            due_date__gte=ctx.today, due_date__lte=horizon, estimated_minutes__isnull=False
        ).values_list('due_date', 'estimated_minutes'):
            minutes[due] = minutes.get(due, 0) + est
        days = []
        for offset in range(7):
            day = ctx.today + timedelta(days=offset)
            row = rows.get(day)
            days.append({
                'date': day.isoformat(),
                'tasks': row['n'] if row else 0,
                'estimated_minutes': minutes.get(day, 0),
                'tasks_without_estimate': row['unestimated'] if row else 0,
            })
        return {'next_7_days': days}
