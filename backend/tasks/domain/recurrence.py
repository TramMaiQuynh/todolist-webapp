import calendar
from abc import ABC, abstractmethod
from datetime import date, timedelta


class RecurrenceRule(ABC):
    """Strategy: cách tính ngày xuất hiện kế tiếp của một công việc lặp."""

    key = ''
    label = ''

    @abstractmethod
    def next_date(self, current: date, interval: int) -> date:
        ...


class DailyRule(RecurrenceRule):
    key = 'daily'
    label = 'Daily'

    def next_date(self, current, interval):
        return current + timedelta(days=interval)


class WeeklyRule(RecurrenceRule):
    key = 'weekly'
    label = 'Weekly'

    def next_date(self, current, interval):
        return current + timedelta(weeks=interval)


def _add_months(current: date, months: int) -> date:
    index = current.month - 1 + months
    year, month = current.year + index // 12, index % 12 + 1
    day = min(current.day, calendar.monthrange(year, month)[1])  # 31/01 -> 28|29/02
    return date(year, month, day)


class MonthlyRule(RecurrenceRule):
    key = 'monthly'
    label = 'Monthly'

    def next_date(self, current, interval):
        return _add_months(current, interval)


class YearlyRule(RecurrenceRule):
    key = 'yearly'
    label = 'Yearly'

    def next_date(self, current, interval):
        return _add_months(current, 12 * interval)


class RecurrenceRegistry:
    """Registry: thêm quy tắc lặp mới bằng register(), không phải sửa code cũ."""

    def __init__(self, rules=()):
        self._rules = {}
        for rule in rules:
            self.register(rule)

    def register(self, rule: RecurrenceRule):
        self._rules[rule.key] = rule

    def get(self, key):
        return self._rules.get(key)

    def keys(self):
        return list(self._rules)

    def choices(self):
        return [{'key': r.key, 'label': r.label} for r in self._rules.values()]


def build_default_registry():
    return RecurrenceRegistry([DailyRule(), WeeklyRule(), MonthlyRule(), YearlyRule()])
