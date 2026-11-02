from datetime import datetime, time, timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from tasks.models import Category, Task
from tasks.statistics import StatsContext, build_default_metric_registry
from tasks.statistics.base import Metric, MetricRegistry
from tasks.tests.helpers import days_from_today, make_task, make_user, today


def complete(task, days_ago):
    """Đặt completed_at về `days_ago` ngày trước (bỏ qua save() tự gán)."""
    when = timezone.now() - timedelta(days=days_ago)
    Task.objects.filter(pk=task.pk).update(status=Task.COMPLETED, completed_at=when)


def compute(user, days=30):
    all_tasks = Task.objects.filter(owner=user)
    ctx = StatsContext(all_tasks, all_tasks.filter(archived_at__isnull=True), today(), days)
    return build_default_metric_registry().compute_all(ctx)


class StatisticsTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_empty_account(self):
        stats = compute(self.user)
        self.assertEqual(stats['overview']['total'], 0)
        self.assertEqual(stats['overview']['completion_rate'], 0.0)
        self.assertEqual(len(stats['trend']['series']), 30)

    def test_overview_and_deadlines(self):
        make_task(self.user, due_date=days_from_today(-1))   # quá hạn
        make_task(self.user, due_date=today())               # hôm nay
        make_task(self.user, due_date=days_from_today(3))    # 7 ngày tới
        make_task(self.user)                                 # không hạn
        done = make_task(self.user, due_date=days_from_today(-9))
        complete(done, 0)                                    # xong -> không tính quá hạn
        make_task(self.user, due_date=days_from_today(-9), archived_at=timezone.now())  # bỏ qua
        stats = compute(self.user)
        self.assertEqual(stats['overview']['total'], 5)
        self.assertEqual(stats['overview']['by_status']['Completed'], 1)
        self.assertEqual(stats['overview']['completion_rate'], 20.0)
        self.assertEqual(stats['deadlines'], {
            'overdue': 1, 'due_today': 1, 'due_next_7_days': 1, 'no_due_date': 1})

    def test_stats_exclude_other_users(self):
        make_task(make_user('bob'))
        self.assertEqual(compute(self.user)['overview']['total'], 0)

    def test_breakdown(self):
        work = Category.objects.get(name='Work', owner__isnull=True)
        make_task(self.user, priority='High', category=work)
        make_task(self.user, priority='High')
        stats = compute(self.user)['breakdown']
        self.assertEqual(stats['open_by_priority']['High'], 2)
        self.assertCountEqual(
            stats['open_by_category'],
            [{'category': 'Work', 'count': 1}, {'category': 'Uncategorized', 'count': 1}])

    def test_trend_counts_completions_per_day(self):
        complete(make_task(self.user), 0)
        complete(make_task(self.user), 0)
        complete(make_task(self.user), 2)
        series = {p['date']: p for p in compute(self.user, days=7)['trend']['series']}
        self.assertEqual(series[today().isoformat()]['completed'], 2)
        self.assertEqual(series[days_from_today(-2).isoformat()]['completed'], 1)

    def test_performance_on_time_rate(self):
        on_time = make_task(self.user, due_date=days_from_today(2))
        late = make_task(self.user, due_date=days_from_today(-5))
        complete(on_time, 0)
        complete(late, 0)
        perf = compute(self.user)['performance']
        self.assertEqual(perf['completed_in_window'], 2)
        self.assertEqual(perf['on_time_rate'], 50.0)

    def test_performance_uses_configured_local_date(self):
        task = make_task(self.user, due_date=today())
        local_midnight = timezone.make_aware(
            datetime.combine(today(), time.min), timezone.get_current_timezone()
        )
        Task.objects.filter(pk=task.pk).update(
            status=Task.COMPLETED, completed_at=local_midnight
        )
        self.assertEqual(compute(self.user)['performance']['on_time_rate'], 100.0)

    def test_workload_sums_estimates(self):
        make_task(self.user, due_date=today(), estimated_minutes=30)
        make_task(self.user, due_date=today(), estimated_minutes=45)
        make_task(self.user, due_date=today())
        day0 = compute(self.user)['workload']['next_7_days'][0]
        self.assertEqual(
            (day0['tasks'], day0['estimated_minutes'], day0['tasks_without_estimate']), (3, 75, 1))

    def test_registry_accepts_new_metric(self):
        class Always42(Metric):
            key = 'answer'

            def compute(self, ctx):
                return {'value': 42}

        ctx = StatsContext(Task.objects.none(), Task.objects.none(), today(), 7)
        self.assertEqual(MetricRegistry([Always42()]).compute_all(ctx), {'answer': {'value': 42}})

    def test_statistics_endpoint_validates_days(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.user).key}')
        response = client.get('/api/v1/tasks/statistics/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('forecast', response.data)
        self.assertEqual(client.get('/api/v1/tasks/statistics/?days=0').status_code, 400)
        self.assertEqual(client.get('/api/v1/tasks/statistics/?days=abc').status_code, 400)
