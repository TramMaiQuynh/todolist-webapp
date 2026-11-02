import django_filters as df
from django.db.models import Q
from django.utils import timezone

from tasks.models import Task


class CharInFilter(df.BaseInFilter, df.CharFilter):
    """Cho phép ?status=Pending,In_progress"""


class NumberInFilter(df.BaseInFilter, df.NumberFilter):
    """Cho phép ?tags=1,2,3"""


class TaskFilter(df.FilterSet):
    status = CharInFilter(field_name='status', lookup_expr='in')
    priority = CharInFilter(field_name='priority', lookup_expr='in')
    category = NumberInFilter(field_name='category', lookup_expr='in')
    tags = NumberInFilter(field_name='tags', lookup_expr='in', distinct=True)
    due_before = df.DateFilter(field_name='due_date', lookup_expr='lte')
    due_after = df.DateFilter(field_name='due_date', lookup_expr='gte')
    overdue = df.BooleanFilter(method='filter_overdue')
    due_today = df.BooleanFilter(method='filter_due_today')
    no_due_date = df.BooleanFilter(field_name='due_date', lookup_expr='isnull')
    top_level = df.BooleanFilter(field_name='parent', lookup_expr='isnull')
    recurring = df.BooleanFilter(method='filter_recurring')
    archived = df.ChoiceFilter(
        choices=[('true', 'true'), ('false', 'false'), ('all', 'all')],
        method='filter_archived',
    )

    class Meta:
        model = Task
        fields = ['is_important', 'parent']

    @staticmethod
    def _today():
        return timezone.localdate()

    def filter_overdue(self, queryset, name, value):
        overdue = Q(due_date__lt=self._today()) & ~Q(status=Task.COMPLETED)
        return queryset.filter(overdue) if value else queryset.exclude(overdue)

    def filter_due_today(self, queryset, name, value):
        today = Q(due_date=self._today())
        return queryset.filter(today) if value else queryset.exclude(today)

    def filter_recurring(self, queryset, name, value):
        recurring = ~Q(recurrence_frequency='')
        return queryset.filter(recurring) if value else queryset.filter(recurrence_frequency='')

    def filter_archived(self, queryset, name, value):
        if value == 'all':
            return queryset
        if value == 'true':
            return queryset.filter(archived_at__isnull=False)
        return queryset.filter(archived_at__isnull=True)
